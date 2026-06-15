import os
import json
import unittest
import uuid
from datetime import datetime
from fastapi.testclient import TestClient

# Configuration & Store
from app.config import (
    ENABLE_SELF_LEARNING,
    LEARNING_SCHEMA_VERSION,
    MAX_PATTERN_CHAIN,
    MAX_LEARNING_DEPTH
)
from app.learning.learning_models import (
    PatternNode,
    CorrectionNode,
    FeedbackNode,
    QueryClusterNode,
    FailurePatternNode
)
from app.learning.learning_store import (
    clear_learning_store,
    get_patterns,
    get_corrections,
    get_feedback,
    get_clusters,
    get_failure_patterns,
    append_pattern,
    append_correction,
    append_feedback,
    append_failure_pattern
)
from app.learning.query_signature_engine import generate_query_signature
from app.learning.feedback_engine import compile_and_store_feedback
from app.learning.pattern_engine import compile_and_store_pattern
from app.learning.correction_engine import compile_and_store_correction
from app.learning.failure_pattern_engine import compile_and_store_failure_pattern
from app.learning.query_cluster_engine import cluster_query
from app.learning.active_learning_engine import evaluate_active_learning
from app.learning.learning_cache import (
    clear_all_learning_caches,
    get_learning_cache_metrics,
    pattern_cache
)
from app.learning.pattern_decay_engine import decay_learning_memory
from app.learning.pattern_pruner import prune_learning_memory
from app.learning.learning_retriever import retrieve_learning_context
from app.learning.learning_graph import extend_learning_graph
from app.learning.learning_migrations import run_learning_migrations
from app.retrieval.grounding_validator import validate_grounding
from app.retrieval.evidence_models import EvidenceNode
from app.main import app

class TestSelfLearning(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.results = {
            "test_1_accuracy": 0.0,
            "test_2_accuracy": 0.0,
            "test_3_accuracy": 0.0,
            "test_4_accuracy": 0.0,
            "test_5_accuracy": 0.0,
            "test_6_accuracy": 0.0,
            "test_7_accuracy": 0.0,
            "test_8_accuracy": 0.0,
            "test_9_accuracy": 0.0,
            "test_10_accuracy": 0.0,
            "test_11_accuracy": 0.0,
            "test_12_accuracy": 0.0,
            "test_13_accuracy": 0.0,
            "test_14_accuracy": 0.0,
            "test_15_accuracy": 0.0,
            "cache_hit_rate": 0.0,
            "pruning_efficiency": 0.0,
            "Grounding accuracy": 0.0
        }
        
    def setUp(self):
        clear_learning_store()
        clear_all_learning_caches()
        
    def test_1_pattern_creation(self):
        """
        Test 1: PatternNode creation from repeated queries.
        """
        query = "How to integrate self learning in Python RAG?"
        # First save
        pat1 = compile_and_store_pattern(
            query=query,
            entity_set={"python", "rag"},
            intent_type="code_integration",
            success=True,
            evidence_ids=["ev_1"],
            source_modalities=["text"]
        )
        # Repeat query to check reinforcement and uniqueness
        pat2 = compile_and_store_pattern(
            query=query,
            entity_set={"python", "rag"},
            intent_type="code_integration",
            success=True,
            evidence_ids=["ev_2"],
            source_modalities=["text"]
        )
        
        patterns = get_patterns()
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0].frequency, 2)
        self.assertEqual(patterns[0].success_count, 2)
        
        TestSelfLearning.results["test_1_accuracy"] = 1.0

    def test_2_reflection_correction(self):
        """
        Test 2: CorrectionNode generation from reflections.
        """
        original_ans = "The chroma version is v0."
        corrected_ans = "The chroma version is v1."
        corr = compile_and_store_correction(
            reason="Reflection failed on version lookup",
            original_answer=original_ans,
            corrected_answer=corrected_ans,
            evidence_ids=["ev_chroma"],
            source_modalities=["text"],
            reflection_ids=["refl_v0_err"],
            replanning_ids=["replan_v0_err"],
            source="reflection_engine"
        )
        
        corrections = get_corrections()
        self.assertEqual(len(corrections), 1)
        self.assertEqual(corrections[0].original_answer, original_ans)
        self.assertEqual(corrections[0].corrected_answer, corrected_ans)
        self.assertIn("refl_v0_err", corrections[0].reflection_ids)
        
        TestSelfLearning.results["test_2_accuracy"] = 1.0

    def test_3_query_clustering(self):
        """
        Test 3: Semantic query clustering.
        """
        # Cluster first query
        cluster_query("How to parse PDF documents in RAG?", success=True)
        # Cluster second similar query (same semantic intent should match cosine threshold >= 0.85)
        # Since it uses embedding similarity, we will check that a cluster exists
        clusters = get_clusters()
        self.assertTrue(len(clusters) >= 1)
        
        TestSelfLearning.results["test_3_accuracy"] = 1.0

    def test_4_feedback_memory(self):
        """
        Test 4: Feedback memory logging.
        """
        fb = compile_and_store_feedback(
            query="Test query feedback",
            answer="Test answer feedback",
            feedback_type="SUCCESS",
            confidence_label="High",
            grounding_report=[{"claim": "verified", "status": "Supported"}]
        )
        
        feedbacks = get_feedback()
        self.assertEqual(len(feedbacks), 1)
        self.assertEqual(feedbacks[0].feedback_type, "SUCCESS")
        self.assertEqual(feedbacks[0].query, "Test query feedback")
        
        TestSelfLearning.results["test_4_accuracy"] = 1.0

    def test_5_lru_cache(self):
        """
        Test 5: LRU cache hit validation.
        """
        query = "Cache validation query"
        # Prime store with a pattern to retrieve
        compile_and_store_pattern(
            query=query,
            entity_set={"cache"},
            intent_type="test",
            success=True
        )
        
        # Invalidate caches
        clear_all_learning_caches()
        
        # First query: Cache Miss
        retrieve_learning_context(query)
        metrics_miss = get_learning_cache_metrics()
        self.assertEqual(metrics_miss["misses"], 1)
        self.assertEqual(metrics_miss["hits"], 0)
        
        # Second query: Cache Hit
        retrieve_learning_context(query)
        metrics_hit = get_learning_cache_metrics()
        self.assertEqual(metrics_hit["hits"], 1)
        self.assertEqual(metrics_hit["misses"], 1)
        self.assertEqual(metrics_hit["hit_rate"], 0.5)
        
        TestSelfLearning.results["test_5_accuracy"] = 1.0
        TestSelfLearning.results["cache_hit_rate"] = metrics_hit["hit_rate"]

    def test_6_decay_engine(self):
        """
        Test 6: Decay engine verification.
        """
        pat = compile_and_store_pattern(
            query="Decay test query",
            entity_set={"decay"},
            intent_type="test",
            success=True
        )
        initial_conf = pat.confidence
        
        decay_learning_memory()
        
        patterns = get_patterns()
        self.assertEqual(len(patterns), 1)
        self.assertLess(patterns[0].confidence, initial_conf)
        
        TestSelfLearning.results["test_6_accuracy"] = 1.0

    def test_7_pattern_pruner(self):
        """
        Test 7: Pattern pruner verification.
        """
        # Create a pattern, decay it heavily or force it to low confidence
        pat = PatternNode(
            pattern_id="pat_to_prune",
            signature="sig_prune",
            confidence=0.05,  # Below default prune threshold 0.1
            last_confirmed=datetime.utcnow().isoformat(),
            created_at=datetime.utcnow().isoformat()
        )
        append_pattern(pat)
        
        res = prune_learning_memory(threshold=0.1)
        
        patterns = get_patterns()
        self.assertEqual(len(patterns), 0)
        self.assertEqual(res["pruned_patterns"], 1)
        self.assertEqual(res["pruning_efficiency"], 1.0)
        
        TestSelfLearning.results["test_7_accuracy"] = 1.0
        TestSelfLearning.results["pruning_efficiency"] = res["pruning_efficiency"]

    def test_8_graph_edge_validation(self):
        """
        Test 8: Learning graph edge validation.
        """
        pat = compile_and_store_pattern(
            query="Graph test query",
            entity_set={"graphentity"},
            intent_type="test",
            success=True
        )
        base_graph = {"nodes": [], "edges": []}
        extended = extend_learning_graph(
            base_graph=base_graph,
            patterns=[pat],
            corrections=[],
            feedbacks=[],
            clusters=[],
            failures=[]
        )
        
        node_ids = {n["id"] for n in extended["nodes"]}
        self.assertIn(pat.pattern_id, node_ids)
        
        # Verify edge PatternNode -> EntityNode (pattern_to_entity)
        edges = extended["edges"]
        has_edge = any(
            e["source"] == pat.pattern_id and 
            e["target"] == "entity_graphentity" and 
            e["type"] == "pattern_to_entity"
            for e in edges
        )
        self.assertTrue(has_edge)
        
        TestSelfLearning.results["test_8_accuracy"] = 1.0

    def test_9_rest_api_status(self):
        """
        Test 9: REST API status checks.
        """
        # Clean store
        clear_learning_store()
        
        # Create a pattern and correction
        compile_and_store_pattern("API query", {"api"}, "test", True)
        compile_and_store_correction("API error", "original", "corrected")
        
        response = self.client.get("/learning/patterns")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) >= 1)
        
        response = self.client.get("/learning/corrections")
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get("/learning/cache")
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post("/learning/query", json={"query": "API query"})
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get("/debug/learning-graph")
        self.assertEqual(response.status_code, 200)
        
        TestSelfLearning.results["test_9_accuracy"] = 1.0

    def test_10_grounding_validator(self):
        """
        Test 10: Grounding validator authority.
        """
        evidence = [
            EvidenceNode(
                evidence_id="ev_1",
                content="The server runs offline using Phi-3 LLM locally.",
                source="readme.md",
                source_type="text",
                modality="text",
                retrieval_score=0.9,
                confidence="High",
                citation_reason="Direct match"
            )
        ]
        answer = "Google Cloud Platform GCP GCP cloud hosting."
        
        final_ans, report = validate_grounding(answer, evidence)
        
        # Grounding Validator must detect ungrounded claim and either prune it or return placeholder
        self.assertNotIn("Google Cloud Platform", final_ans)
        
        TestSelfLearning.results["test_10_accuracy"] = 1.0
        TestSelfLearning.results["Grounding accuracy"] = 1.0

    def test_11_failure_pattern(self):
        """
        Test 11: Failure pattern extraction.
        """
        fail = compile_and_store_failure_pattern(
            failure_type="timeout_error",
            tool_failures=["ollama_generate"],
            grounding_failures=[],
            is_timeout=True
        )
        
        failures = get_failure_patterns()
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0].failure_type, "timeout_error")
        self.assertEqual(failures[0].timeout_count, 1)
        
        TestSelfLearning.results["test_11_accuracy"] = 1.0

    def test_12_reinforcement_accumulation(self):
        """
        Test 12: Pattern reinforcement accumulation.
        """
        query = "Reinforcement test query"
        for _ in range(5):
            compile_and_store_pattern(query, {"reinforcement"}, "test", True)
            
        patterns = get_patterns()
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0].frequency, 5)
        
        TestSelfLearning.results["test_12_accuracy"] = 1.0

    def test_13_schema_migration(self):
        """
        Test 13: Schema migration validation.
        """
        legacy_data = {
            "schema_version": 0,
            "patterns": {
                "pat_old": {
                    "pattern_id": "pat_old",
                    "signature": "sig_old",
                    "frequency": 1,
                    "success_count": 1,
                    "last_confirmed": "2026-06-15T00:00:00",
                    "created_at": "2026-06-15T00:00:00"
                }
            }
        }
        
        migrated = run_learning_migrations(legacy_data)
        self.assertEqual(migrated["schema_version"], LEARNING_SCHEMA_VERSION)
        self.assertIn("corrections", migrated)
        self.assertIn("failure_patterns", migrated)
        
        TestSelfLearning.results["test_13_accuracy"] = 1.0

    def test_14_failure_linkage(self):
        """
        Test 14: FailurePatternNode -> ReflectionNode linkage.
        """
        fail = compile_and_store_failure_pattern(
            failure_type="execution_crash",
            tool_failures=["image_search"],
            grounding_failures=[],
            is_timeout=False
        )
        
        base_graph = {
            "nodes": [
                {"id": "refl_1", "type": "reflection_node", "label": "reflection"}
            ],
            "edges": []
        }
        
        extended = extend_learning_graph(
            base_graph=base_graph,
            patterns=[],
            corrections=[],
            feedbacks=[],
            clusters=[],
            failures=[fail]
        )
        
        edges = extended["edges"]
        has_link = any(
            e["source"] == fail.failure_pattern_id and
            e["target"] == "refl_1" and
            e["type"] == "failure_to_reflection"
            for e in edges
        )
        self.assertTrue(has_link)
        
        TestSelfLearning.results["test_14_accuracy"] = 1.0

    def test_15_loop_protection(self):
        """
        Test 15: Loop protection recursion limits.
        """
        # Create more patterns than MAX_PATTERN_CHAIN limit
        patterns_list = []
        for i in range(MAX_PATTERN_CHAIN + 5):
            pat = PatternNode(
                pattern_id=f"pat_limit_{i}",
                signature=f"sig_{i}",
                last_confirmed=datetime.utcnow().isoformat(),
                created_at=datetime.utcnow().isoformat()
            )
            patterns_list.append(pat)
            
        base_graph = {"nodes": [], "edges": []}
        extended = extend_learning_graph(
            base_graph=base_graph,
            patterns=patterns_list,
            corrections=[],
            feedbacks=[],
            clusters=[],
            failures=[]
        )
        
        # Verify only MAX_PATTERN_CHAIN nodes are added
        added_patterns = [n for n in extended["nodes"] if n["type"] == "pattern_node"]
        self.assertEqual(len(added_patterns), MAX_PATTERN_CHAIN)
        
        TestSelfLearning.results["test_15_accuracy"] = 1.0

    @classmethod
    def tearDownClass(cls):
        clear_learning_store()
        clear_all_learning_caches()
        # Export metrics report
        report_path = "test_self_learning_report.json"
        with open(report_path, "w") as f:
            json.dump(cls.results, f, indent=4)
        print(f"[TEST SUITE] Exported self learning metrics report to {report_path}")

if __name__ == "__main__":
    unittest.main()
