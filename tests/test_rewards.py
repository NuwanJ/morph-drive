import unittest
import numpy as np

from morph_drive.rewards.BasicRewardCalculator import BasicRewardCalculator

class TestBasicRewardCalculator(unittest.TestCase):

    def test_calculate_reward_simple(self):
        calculator = BasicRewardCalculator(target_position=np.array([1, 1, 1]))
        current_position = np.array([0, 0, 0])
        reward = calculator.calculate_reward(current_position, None, None, None)
        # Expected reward is negative distance
        expected_reward = -np.linalg.norm(current_position - np.array([1,1,1]))
        self.assertEqual(reward, expected_reward)

    def test_calculate_reward_target_reached(self):
        calculator = BasicRewardCalculator(target_position=np.array([0.5, 0.5, 0.5]))
        current_position = np.array([0.5, 0.5, 0.5])
        reward = calculator.calculate_reward(current_position, None, None, None)
        self.assertEqual(reward, 0)

if __name__ == '__main__':
    unittest.main()
