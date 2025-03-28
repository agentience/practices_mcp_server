#!/usr/bin/env python
"""
Simple test to verify our keyword-only argument pattern.
"""

import unittest
import inspect

class TestKeywordOnlyPattern(unittest.TestCase):
    """Test the keyword-only argument pattern we're using for MCP tools."""

    def test_keyword_only_pattern(self):
        """Test that functions with keyword-only arguments work correctly."""
        # Define a function with keyword-only arguments
        async def test_func(*, arg1: str, arg2: int = 42):
            return f"{arg1}-{arg2}"
        
        # Verify that the signature has keyword-only args
        sig = inspect.signature(test_func)
        
        # Check that all parameters are keyword-only
        for name, param in sig.parameters.items():
            self.assertEqual(param.kind, inspect.Parameter.KEYWORD_ONLY,
                          f"Parameter {name} is not keyword-only")
        
        # Verify the correct parameter names and defaults
        self.assertIn('arg1', sig.parameters)
        self.assertIn('arg2', sig.parameters)
        self.assertEqual(sig.parameters['arg2'].default, 42)
        
        # Prove that it prevents calls with positional args
        with self.assertRaises(TypeError):
            # This should fail because we're passing positional args
            test_func("test", 123)

    def test_our_pattern_matches_pydantic_basemodel(self):
        """
        Verify our approach of using keyword-only arguments for MCP tool methods
        would fix the BaseModel.__init__() issue.
        """
        # Simulate the error context:
        # BaseModel.__init__() takes 1 positional argument but 2 were given
        
        class BaseModel:
            def __init__(self, **kwargs):
                # This init only accepts keyword arguments
                # Simulating Pydantic's BaseModel behavior
                self.data = kwargs
        
        # This should fail with positional args, like the MCP tool functions were
        with self.assertRaises(TypeError):
            model = BaseModel("will fail")  
        
        # This works with keyword args, which is what our fix ensures for MCP tools
        model = BaseModel(field="works fine")
        self.assertEqual(model.data["field"], "works fine")

if __name__ == "__main__":
    unittest.main()
