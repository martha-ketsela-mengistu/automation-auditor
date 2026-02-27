import unittest
from unittest.mock import MagicMock, patch
from src.state import AgentState, Evidence, JudicialOpinion
from src.nodes.judges import prosecutor_node, defense_node, tech_lead_node

class TestJudges(unittest.TestCase):
    def setUp(self):
        # Create a mock state with some evidence
        self.state: AgentState = {
            "repo_url": "https://github.com/test/repo",
            "pdf_path": "test.pdf",
            "rubric_dimensions": [],
            "evidences": {
                "git_forensic_analysis": [
                    Evidence(
                        goal="Verify commit progression",
                        found=True,
                        content="Initial commit -> Tooling -> Graph",
                        location="git log",
                        rationale="A clear progression exists.",
                        confidence=1.0
                    )
                ]
            },
            "opinions": [],
            "final_report": None
        }

    @patch("src.nodes.judges.llm")
    def test_prosecutor_node(self, mock_llm):
        """Test that the prosecutor node returns structured opinions."""
        # Mock the structured LLM behavior
        # We need to mock .with_structured_output().invoke()
        mock_opinion = JudicialOpinion(
            judge="Prosecutor",
            criterion_id="git_forensic_analysis",
            score=2,
            argument="Evidence is too thin, looks like a bulk upload.",
            cited_evidence=["git log"]
        )
        
        mock_structured_llm = MagicMock()
        mock_structured_llm.invoke.return_value = mock_opinion
        mock_llm.with_structured_output.return_value = mock_structured_llm

        # Run the node
        result = prosecutor_node(self.state)

        # Assertions
        self.assertIn("opinions", result)
        self.assertIsInstance(result["opinions"], list)
        
        # Should have opinions for all rubric dimensions (10 in currently loaded rubric)
        # We can check if at least the mock was called
        self.assertTrue(len(result["opinions"]) > 0)
        self.assertEqual(result["opinions"][0].judge, "Prosecutor")

    @patch("src.nodes.judges.llm")
    def test_defense_node(self, mock_llm):
        """Test that the defense node returns structured opinions."""
        mock_opinion = JudicialOpinion(
            judge="Defense",
            criterion_id="git_forensic_analysis",
            score=5,
            argument="The developer showed great effort in structuring the history.",
            cited_evidence=["git log"]
        )
        
        mock_structured_llm = MagicMock()
        mock_structured_llm.invoke.return_value = mock_opinion
        mock_llm.with_structured_output.return_value = mock_structured_llm

        result = defense_node(self.state)

        self.assertIn("opinions", result)
        self.assertEqual(result["opinions"][0].judge, "Defense")

    @patch("src.nodes.judges.llm")
    def test_tech_lead_node(self, mock_llm):
        """Test that the tech lead node returns structured opinions."""
        mock_opinion = JudicialOpinion(
            judge="TechLead",
            criterion_id="git_forensic_analysis",
            score=4,
            argument="Maintainable and clear, though could use more documentation.",
            cited_evidence=["git log"]
        )
        
        mock_structured_llm = MagicMock()
        mock_structured_llm.invoke.return_value = mock_opinion
        mock_llm.with_structured_output.return_value = mock_structured_llm

        result = tech_lead_node(self.state)

        self.assertIn("opinions", result)
        self.assertEqual(result["opinions"][0].judge, "TechLead")

if __name__ == "__main__":
    unittest.main()
