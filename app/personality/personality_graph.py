from typing import Dict, List, Set, Any, Optional

from app.config import MAX_PERSONALITY_DEPTH, MAX_TOTAL_PERSONALITIES_VISITED
from app.personality.personality_store import (
    get_preferences,
    get_user_styles,
    get_adaptive_personalities,
    get_interaction_memories,
    get_recommendation_memories
)

class GraphNode:
    def __init__(self, node_id: str, type: str, data: Dict[str, Any]):
        self.node_id = node_id
        self.type = type
        self.data = data
        self.neighbors: Set[str] = set()

class PersonalityGraph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}

    def add_node(self, node_id: str, type: str, data: Dict[str, Any]):
        if node_id not in self.nodes:
            self.nodes[node_id] = GraphNode(node_id, type, data)

    def add_edge(self, source_id: str, target_id: str):
        if source_id in self.nodes and target_id in self.nodes:
            self.nodes[source_id].neighbors.add(target_id)
            self.nodes[target_id].neighbors.add(source_id)

def build_personality_graph() -> PersonalityGraph:
    """
    Constructs a graph from the active personality store, linking:
    Preferences -> Styles,
    Preferences -> Adaptive Personalities,
    Preferences -> Interactions,
    Interactions -> Recommendations,
    Personalities -> Recommendations.
    """
    graph = PersonalityGraph()

    # Retrieve all nodes
    prefs = get_preferences()
    styles = get_user_styles()
    personalities = get_adaptive_personalities()
    interactions = get_interaction_memories()
    recommendations = get_recommendation_memories()

    # Add all nodes to graph
    for p in prefs:
        graph.add_node(p.preference_id, "preference", p.model_dump())
    for s in styles:
        graph.add_node(s.style_id, "style", s.model_dump())
    for ap in personalities:
        graph.add_node(ap.personality_id, "personality", ap.model_dump())
    for i in interactions:
        graph.add_node(i.interaction_id, "interaction", i.model_dump())
    for r in recommendations:
        graph.add_node(r.recommendation_id, "recommendation", r.model_dump())

    # Create Edges based on attributes
    # 1. Preferences -> Styles (matching tone_preference vs writing_style)
    for p in prefs:
        for s in styles:
            if p.tone_preference.lower() in s.writing_style.lower() or s.writing_style.lower() in p.tone_preference.lower():
                graph.add_edge(p.preference_id, s.style_id)

    # 2. Preferences -> Personalities (matching explanation_depth vs explanation_preferences)
    for p in prefs:
        for ap in personalities:
            # Match explanation_depth
            if any(p.explanation_depth.lower() in exp.lower() for exp in ap.explanation_preferences):
                graph.add_edge(p.preference_id, ap.personality_id)

    # 3. Preferences -> Interactions (matching domains or entities)
    for p in prefs:
        for i in interactions:
            domain_match = any(d.lower() in i.topic.lower() for d in p.preferred_domains)
            entity_match = any(e.lower() in i.topic.lower() for e in p.user_entities)
            if domain_match or entity_match:
                graph.add_edge(p.preference_id, i.interaction_id)

    # 4. Interactions -> Recommendations (matching topic/domain to recommendation categories/items)
    for i in interactions:
        for r in recommendations:
            if i.topic.lower() in r.category.lower() or r.category.lower() in i.topic.lower():
                graph.add_edge(i.interaction_id, r.recommendation_id)
            elif i.topic.lower() in r.item.lower() or r.item.lower() in i.topic.lower():
                graph.add_edge(i.interaction_id, r.recommendation_id)

    # 5. Personalities -> Recommendations (matching speaker patterns or explanation styles)
    for ap in personalities:
        for r in recommendations:
            if ap.personality_type.lower() in r.category.lower():
                graph.add_edge(ap.personality_id, r.recommendation_id)

    return graph

def traverse_graph(
    graph: PersonalityGraph,
    start_id: str,
    target_type: str,
    visited: Optional[Set[str]] = None,
    depth: int = 0
) -> List[Dict[str, Any]]:
    """
    Traverses the graph starting from start_id up to MAX_PERSONALITY_DEPTH.
    Finds and returns nodes of target_type, preventing cycles via visited sets.
    """
    if visited is None:
        visited = set()

    if start_id not in graph.nodes:
        return []

    if depth >= MAX_PERSONALITY_DEPTH or len(visited) >= MAX_TOTAL_PERSONALITIES_VISITED:
        return []

    visited.add(start_id)
    results = []

    node = graph.nodes[start_id]
    if node.type == target_type:
        results.append(node.data)

    # Traverse neighbors
    for neighbor_id in node.neighbors:
        if neighbor_id not in visited:
            results.extend(traverse_graph(graph, neighbor_id, target_type, visited, depth + 1))

    return results

def get_recommendations_for_preference(preference_id: str) -> List[Dict[str, Any]]:
    """
    Traces paths from a preference node down to recommendation nodes.
    """
    graph = build_personality_graph()
    visited = set()
    return traverse_graph(graph, preference_id, "recommendation", visited, 0)
