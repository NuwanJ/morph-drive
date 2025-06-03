import unittest
import numpy as np

from morph_drive.policy.do_nothing import DoNothingPolicy

class TestDoNothingPolicy(unittest.TestCase):

    def test_get_action_returns_zero_array(self):
        policy = DoNothingPolicy(action_size=3)
        observation = np.array([1, 2, 3])
        action = policy.get_action(observation)
        self.assertTrue(np.array_equal(action, np.zeros(3)))

    def test_get_action_with_different_action_size(self):
        policy = DoNothingPolicy(action_size=5)
        observation = np.array([1, 2, 3, 4, 5])
        action = policy.get_action(observation)
        self.assertTrue(np.array_equal(action, np.zeros(5)))

if __name__ == '__main__':
    unittest.main()
