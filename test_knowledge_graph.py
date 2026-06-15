import os
import json
import unittest
import uuid
from datetime import datetime
from fastapi.testclient import TestClient

# Core KG imports
from app.config import (
    ENABLE_KNOWLEDGE_GRAPH,
    GRAPH_SCHEMA_VERSION,
    RELATION_DECAY_FACTOR,
    ENTITY_DECAY_FACTOR
)
from app.retrieval.knowledge_models import EntityNode, RelationNode, TemporalNode
from app.retrieval.graph_store import (
    clear_graph_store,
    get_entities,
    get_relations,
    get_temporal_events,
    get_communities,
    append_entities,
    append_relations,
    append_temporal_event,
    load_graph
)
from app.retrieval.entity_alias_registry import normalize_entity_name
from app.retrieval.entity_extractor import build_or_update_entity_node
from app.retrieval.relation_extractor import extract_relations_from_text
from app.retrieval.graph_traverser import find_paths
from app.retrieval.graph_query_engine import (
    query_neighbors,
    query_path,
    query_community,
    query_timeline,
    query_similar
)
from app.retrieval.community_detector import detect_communities
from app.retrieval.relation_decay_engine import decay_graph
from app.retrieval.graph_pruner import prune_graph
from app.retrieval.graph_explanation_engine import get_latest_graph_explanation, compile_graph_explanation
from app.retrieval.graph_cache import get_cache_metrics, clear_all_graph_caches
from app.retrieval.grounding_validator import validate_grounding
from app.main import app

class TestKnowledgeGraph(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.results = {
            "test_1_single_hop_accuracy": 0.0,
            "test_2_multi_hop_accuracy": 0.0,
            "test_3_temporal_accuracy": 0.0,
            "test_4_community_accuracy": 0.0,
            "test_5_migration_accuracy": 0.0,
            "test_6_cache_efficiency": 0.0,
            "test_7_pruner_accuracy": 0.0,
            "test_8_api_accuracy": 0.0,
            "test_9_grounding_accuracy": 0.0,
            "pruning_efficiency": 0.0,
            "cache_hit_rate": 0.0
        }
        
    def setUp(self):
        clear_graph_store()
        clear_all_graph_caches()
        
    def test_1_single_hop(self):
        """
        Test 1: Single-hop relation check (ChromaDB -> FastAPI).
        """
        # Append mock entities
        ent_chroma = build_or_update_entity_node(name="ChromaDB")
        ent_fastapi = build_or_update_entity_node(name="FastAPI")
        append_entities([ent_chroma, ent_fastapi])
        
        # Append mock relation
        rel = RelationNode(
            relation_id="rel_chromadb_uses_fastapi",
            source_entity="chromadb",
            target_entity="fastapi",
            relation_type="USES",
            confidence=0.9,
            weight=0.9,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            created_by="test",
            last_confirmed=datetime.utcnow().isoformat(),
            confirmation_count=1
        )
        append_relations([rel])
        
        # Query neighbors
        neighbors = query_neighbors("ChromaDB")
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0]["neighbor"].canonical_name, "fastapi")
        self.assertEqual(neighbors[0]["relation"].relation_type, "USES")
        
        TestKnowledgeGraph.results["test_1_single_hop_accuracy"] = 1.0

    def test_2_multi_hop(self):
        """
        Test 2: Multi-hop path traversal check (ChromaDB -> FastAPI -> Ollama).
        """
        # Append mock entities
        ent_chroma = build_or_update_entity_node(name="ChromaDB")
        ent_fastapi = build_or_update_entity_node(name="FastAPI")
        ent_ollama = build_or_update_entity_node(name="Ollama")
        append_entities([ent_chroma, ent_fastapi, ent_ollama])
        
        # Append mock relations
        rel1 = RelationNode(
            relation_id="rel_chromadb_uses_fastapi",
            source_entity="chromadb",
            target_entity="fastapi",
            relation_type="USES",
            confidence=0.8,
            weight=0.8,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            created_by="test",
            last_confirmed=datetime.utcnow().isoformat(),
            confirmation_count=1
        )
        rel2 = RelationNode(
            relation_id="rel_fastapi_connects_to_ollama",
            source_entity="fastapi",
            target_entity="ollama",
            relation_type="CONNECTS_TO",
            confidence=0.85,
            weight=0.85,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            created_by="test",
            last_confirmed=datetime.utcnow().isoformat(),
            confirmation_count=1
        )
        append_relations([rel1, rel2])
        
        # Find paths
        paths = find_paths("ChromaDB", "Ollama", max_depth=3)
        self.assertGreater(len(paths), 0)
        
        # Verify first path
        path = paths[0]
        # Path format: [EntityNode, RelationNode, EntityNode, RelationNode, EntityNode]
        self.assertEqual(path[0].canonical_name, "chromadb")
        self.assertEqual(path[1].relation_type, "USES")
        self.assertEqual(path[2].canonical_name, "fastapi")
        self.assertEqual(path[3].relation_type, "CONNECTS_TO")
        self.assertEqual(path[4].canonical_name, "ollama")
        
        TestKnowledgeGraph.results["test_2_multi_hop_accuracy"] = 1.0

    def test_3_temporal(self):
        """
        Test 3: Temporal timeline and timestamp updates validation.
        """
        t_node = TemporalNode(
            event_id="evt_test_1",
            description="ChromaDB was initialized in our project",
            timestamp="2026-06-15T12:00:00Z",
            entities=["chromadb"],
            event_type="setup",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            last_seen=datetime.utcnow().isoformat()
        )
        append_temporal_event(t_node)
        
        timeline = query_timeline("ChromaDB")
        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline[0].event_id, "evt_test_1")
        self.assertEqual(timeline[0].event_type, "setup")
        
        TestKnowledgeGraph.results["test_3_temporal_accuracy"] = 1.0

    def test_4_community(self):
        """
        Test 4: Modularity label propagation community clustering checks.
        """
        ent_chroma = build_or_update_entity_node(name="ChromaDB")
        ent_fastapi = build_or_update_entity_node(name="FastAPI")
        ent_ollama = build_or_update_entity_node(name="Ollama")
        append_entities([ent_chroma, ent_fastapi, ent_ollama])
        
        rel1 = RelationNode(
            relation_id="rel_chromadb_uses_fastapi",
            source_entity="chromadb",
            target_entity="fastapi",
            relation_type="USES",
            confidence=0.8,
            weight=0.8,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            created_by="test",
            last_confirmed=datetime.utcnow().isoformat(),
            confirmation_count=1
        )
        rel2 = RelationNode(
            relation_id="rel_fastapi_connects_to_ollama",
            source_entity="fastapi",
            target_entity="ollama",
            relation_type="CONNECTS_TO",
            confidence=0.85,
            weight=0.85,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            created_by="test",
            last_confirmed=datetime.utcnow().isoformat(),
            confirmation_count=1
        )
        append_relations([rel1, rel2])
        
        detect_communities()
        
        comms = get_communities()
        self.assertGreater(len(comms), 0)
        
        # Verify entities now have community IDs
        updated_ents = get_entities()
        has_community = any(ent.community_id is not None for ent in updated_ents)
        self.assertTrue(has_community)
        
        TestKnowledgeGraph.results["test_4_community_accuracy"] = 1.0

    def test_5_migration(self):
        """
        Test 5: Graph store state reload and schema migration validation.
        """
        # Save a legacy v0 schema graph
        legacy_graph = {
            "schema_version": 0,
            "entities": {
                "entity_chromadb": {
                    "entity_id": "entity_chromadb",
                    "name": "ChromaDB",
                    "canonical_name": "chromadb",
                    "entity_type": "conceptual",
                    "created_at": "2026-06-15T10:00:00Z",
                    "updated_at": "2026-06-15T10:00:00Z",
                    "last_seen": "2026-06-15T10:00:00Z"
                }
            }
        }
        
        from app.retrieval.graph_store import GRAPH_FILE_PATH
        with open(GRAPH_FILE_PATH, "w") as f:
            json.dump(legacy_graph, f)
            
        # Trigger load_graph to trigger migration
        loaded = load_graph()
        
        self.assertEqual(loaded.get("schema_version"), 1)
        self.assertIn("relations", loaded)
        self.assertIn("communities", loaded)
        
        TestKnowledgeGraph.results["test_5_migration_accuracy"] = 1.0

    def test_6_cache(self):
        """
        Test 6: Cache performance and latency reduction check.
        """
        ent_chroma = build_or_update_entity_node(name="ChromaDB")
        append_entities([ent_chroma])
        
        # First query (miss)
        query_neighbors("ChromaDB")
        metrics_1 = get_cache_metrics()
        self.assertEqual(metrics_1["misses"], 1)
        
        # Second query (hit)
        query_neighbors("ChromaDB")
        metrics_2 = get_cache_metrics()
        self.assertEqual(metrics_2["hits"], 1)
        self.assertEqual(metrics_2["hit_rate"], 0.5)
        
        TestKnowledgeGraph.results["test_6_cache_efficiency"] = 1.0
        TestKnowledgeGraph.results["cache_hit_rate"] = metrics_2["hit_rate"]

    def test_7_edge_decay_and_pruner(self):
        """
        Test 7: Edge decay and pruner execution checks.
        """
        ent_chroma = build_or_update_entity_node(name="ChromaDB")
        ent_fastapi = build_or_update_entity_node(name="FastAPI")
        append_entities([ent_chroma, ent_fastapi])
        
        # Low weight relation
        rel = RelationNode(
            relation_id="rel_chromadb_uses_fastapi",
            source_entity="chromadb",
            target_entity="fastapi",
            relation_type="USES",
            confidence=0.08,
            weight=0.08,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            created_by="test",
            last_confirmed=datetime.utcnow().isoformat(),
            confirmation_count=1
        )
        append_relations([rel])
        
        # Verify it exists
        self.assertEqual(len(get_relations()), 1)
        
        # Run decay
        decay_graph()
        
        # Verify it decayed
        decayed_rel = get_relations()[0]
        self.assertLess(decayed_rel.weight, 0.08)
        
        # Run pruner with threshold = 0.1
        pruned_stats = prune_graph(weight_threshold=0.1)
        
        self.assertEqual(pruned_stats["pruned_relations"], 1)
        self.assertEqual(len(get_relations()), 0)
        # Verify entities also pruned because degree = 0
        self.assertEqual(len(get_entities()), 0)
        self.assertEqual(pruned_stats["pruned_entities"], 2)
        
        TestKnowledgeGraph.results["test_7_pruner_accuracy"] = 1.0
        TestKnowledgeGraph.results["pruning_efficiency"] = pruned_stats["pruning_efficiency"]

    def test_8_rest_api(self):
        """
        Test 8: REST API status check on all endpoints.
        """
        response_explanation = self.client.get("/debug/graph-explanation")
        self.assertEqual(response_explanation.status_code, 200)
        
        response_graph = self.client.get("/debug/knowledge-graph")
        self.assertEqual(response_graph.status_code, 200)
        
        response_cache = self.client.get("/debug/graph-cache")
        self.assertEqual(response_cache.status_code, 200)
        
        response_clear = self.client.post("/knowledge/clear")
        self.assertEqual(response_clear.status_code, 200)
        
        TestKnowledgeGraph.results["test_8_api_accuracy"] = 1.0

    def test_9_grounding_validator(self):
        """
        Test 9: Grounding validator authority check (London weather fallback).
        """
        from app.retrieval.evidence_models import EvidenceNode
        
        # Mock evidence list without weather info
        evidence = [
            EvidenceNode(
                evidence_id="ev_1",
                content="The project is built using Python, FastAPI, and ChromaDB.",
                source="readme.md",
                source_type="text",
                modality="text",
                retrieval_score=0.9,
                confidence="High",
                citation_reason="Direct match"
            )
        ]
        
        # Answer containing a completely unsupported claim
        unsupported_answer = "The project uses FastAPI. Also, the current weather in London is 22 degrees and sunny."
        
        final_answer, report = validate_grounding(unsupported_answer, evidence)
        
        # Verify that the grounding validator pruned or marked down the unsupported claim
        self.assertNotIn("London", final_answer)
        
        # Verify grounding validator flagged it
        has_refuted = any(item["status"] in ["Refuted", "Unsupported"] for item in report)
        self.assertTrue(has_refuted)
        
        TestKnowledgeGraph.results["test_9_grounding_accuracy"] = 1.0

    @classmethod
    def tearDownClass(cls):
        clear_graph_store()
        clear_all_graph_caches()
        # Export metrics report
        report_path = "test_knowledge_graph_report.json"
        with open(report_path, "w") as f:
            json.dump(cls.results, f, indent=4)
        print(f"[TEST SUITE] Exported knowledge graph metrics report to {report_path}")

if __name__ == "__main__":
    unittest.main()
