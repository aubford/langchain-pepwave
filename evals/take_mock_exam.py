import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from load.batch_manager import BatchManager
from evals.batch_llm import BatchChatOpenAI
from inference.rag_inference import RagInference
from prompts import load_prompts
from langchain_core.prompts import ChatPromptTemplate


class MockExamOutput(BaseModel):
    correct_choices: list[str] = Field(
        description="An array containing the exact text for each correct choice"
    )


PROMPTS = load_prompts()
system_prompt = PROMPTS['ragas_eval/mock_exam_system'].format(
    system_prompt=PROMPTS['inference/system']
)

messages_prompt = ChatPromptTemplate(
    [
        ("system", system_prompt),
        ("human", PROMPTS['ragas_eval/mock_exam_example_query']),
        ("ai", PROMPTS['ragas_eval/mock_exam_example_answer']),
        ("human", "{input}"),
    ]
)


class MockExam:
    def __init__(
        self,
        evals_dir: Path,
        run_name: str,
        llm_model: str,
        pinecone_index_name: str,
        output_dir: Path,
        should_create_batch_job: bool = True,
        sample: Any = False,
    ):
        self.output_dir = output_dir
        runs_dir = evals_dir / "runs"
        self.should_create_batch_job = should_create_batch_job
        self.batch_manager = BatchManager(
            base_path=runs_dir / run_name / "batches",
            endpoint="/v1/chat/completions",
            batch_name="mock_exam_batch",
            schema=MockExamOutput,
        )
        self.rag_inference = RagInference(
            llm_model=llm_model,
            pinecone_index_name=pinecone_index_name,
            messages=messages_prompt,
            eval_llm=BatchChatOpenAI(
                model=llm_model,
                temperature=0,
                batch_manager=self.batch_manager,
            ),
        )
        filename = (
            "certified_engineer_exam_sample.json"
            if sample
            else "certified_engineer_exam.json"
        )
        self.mock_exam_path = evals_dir / "testsets" / filename
        with open(self.mock_exam_path, "r") as f:
            self.mock_exam_questions = json.load(f)

    async def generate_batchfile(self) -> None:
        """
        Run PCE mock exam questions through the RAG system and evaluate results.

        Returns:
            DataFrame with columns: question, answer, correct?, retrieved_contexts
        """
        # Prepare queries (duplicate each question)
        queries = {}
        for q in self.mock_exam_questions:
            choices_text = "\n".join(
                [f"{j+1}. {choice}" for j, choice in enumerate(q["choices"])]
            )
            query = PROMPTS["ragas_eval/mock_exam_query"].format(
                question=q["question"], choices=choices_text
            )
            queries[q["question_id"]] = query

        if self.should_create_batch_job:
            self.batch_manager.clear_batch_files()
        results = await self.rag_inference.batch_query_for_eval(queries)
        for q in self.mock_exam_questions:
            q["custom_id"] = results[q["question_id"]]["answer"]

        with open(self.mock_exam_path, "w") as f:
            json.dump(self.mock_exam_questions, f, indent=2)

        if self.should_create_batch_job:
            self.batch_manager.create_batch_job()

    def get_results(self) -> tuple[str, list[dict[str, str]]]:
        batch_results = self.batch_manager.get_content_if_ready()

        for q in self.mock_exam_questions:
            custom_id = q["custom_id"]
            q["given_answer"] = json.loads(batch_results[custom_id])["correct_choices"]

        correct_count = 0.0
        missed_questions = []
        for q in self.mock_exam_questions:
            given = set(q["given_answer"])
            correct = set(q["correct_answers"])
            if given == correct:
                correct_count += 1
            else:
                if given.issubset(correct) and len(given) > len(correct) / 2:
                    correct_count += 0.5
                missed_questions.append(q)
        # save missed questions
        missed_path = self.output_dir / f"{self.mock_exam_path.stem}_missed.json"
        with open(missed_path, "w") as f:
            json.dump(missed_questions, f)
        return f"{correct_count}/{len(self.mock_exam_questions)}", missed_questions
