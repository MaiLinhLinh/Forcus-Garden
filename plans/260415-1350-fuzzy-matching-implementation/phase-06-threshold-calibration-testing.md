# Phase 06: Threshold Calibration and Testing

## Context Links
- [Research Report](../reports/researcher-260415-1350-fuzzy-string-matching.md)
- [Phase 05](./phase-05-performance-optimization.md)
- [Implementation Plan](../plan.md)

## Overview
**Priority**: High
**Current Status**: Pending
**Description**: Calibrate fuzzy matching thresholds and conduct comprehensive testing to ensure optimal balance between false positives and false negatives.

## Key Insights
- Threshold calibration is critical for user experience
- Real-world testing needed with actual window titles
- Performance vs accuracy trade-off must be balanced
- User feedback loop for continuous improvement

## Requirements
- **Functional**: Optimal threshold setting for minimal false positives
- **Non-functional**: Comprehensive testing with real data
- **Performance**: Maintain 1000+ matches per second

## Architecture
```
Threshold Calibrator → Test Suite → Real-world Data → Performance Analysis → User Feedback
```

## Related Code Files
- **Create**: `tests/test_threshold_calibration.py` - Threshold calibration tests
- **Create**: `utils/threshold_optimizer.py` - Threshold optimization tool
- **Create**: `tests/test_real_world_scenarios.py` - Real-world scenario tests
- **Modify**: `core/tracker.py` - Final threshold integration

## Implementation Steps

1. **Create threshold calibration system**
   ```python
   class ThresholdOptimizer:
       def __init__(self):
           self.threshold = 85  # Default threshold
           self.test_data = []
           self.performance_history = []

       def run_threshold_tests(self, test_data):
           # Test different threshold values
           thresholds = [70, 75, 80, 85, 90, 95, 100]
           results = {}

           for threshold in thresholds:
               matches, false_positives, false_negatives = self._test_threshold(threshold, test_data)
               results[threshold] = {
                   'matches': matches,
                   'false_positives': false_positives,
                   'false_negatives': false_negatives,
                   'precision': matches / (matches + false_positives),
                   'recall': matches / (matches + false_negatives)
               }

           return results

       def recommend_threshold(self, results):
           # Find optimal threshold using F1 score
           best_threshold = 85
           best_f1 = 0

           for threshold, result in results.items():
               f1 = 2 * (result['precision'] * result['recall']) / (result['precision'] + result['recall'])
               if f1 > best_f1:
                   best_f1 = f1
                   best_threshold = threshold

           return best_threshold
   ```

2. **Build comprehensive test suite**
   ```python
   class FuzzyMatcherTestSuite:
       def __init__(self):
           self.test_cases = [
               # Basic cases
               ("vscode", "Visual Studio Code", True),
               ("chrome", "Google Chrome", True),
               ("word", "Microsoft Word", True),

               # Edge cases
               ("vs", "Visual Studio Code", False),  # Should not match by default
               ("code", "Visual Studio Code", False),  # Should not match by default

               # Vietnamese cases
               ("chrome", "Trình duyệt Chrome", True),
               ("word", "Microsoft Word", True),

               # Browser suffixes
               ("github", "GitHub - Google Chrome", True),
               ("slack", "Slack - Google Chrome", True),
           ]

       def run_tests(self, matcher, threshold):
           results = []
           for query, title, expected in self.test_cases:
               result = matcher.fuzzy_match(title, [query], threshold)
               results.append((query, title, expected, result))
           return results
   ```

3. **Create real-world test data**
   ```python
   def generate_real_world_test_data():
       # Common window titles
       test_data = [
           # Development tools
           ("vscode", "Visual Studio Code"),
           ("vscode", "Visual Studio Code - Project File"),
           ("pycharm", "PyCharm 2023.3"),
           ("intellij", "IntelliJ IDEA"),

           # Browsers
           ("chrome", "Google Chrome"),
           ("chrome", "Google Chrome - GitHub"),
           ("chrome", "Google Chrome - Stack Overflow"),
           ("firefox", "Mozilla Firefox"),

           # Communication
           ("discord", "Discord"),
           ("discord", "Discord - Voice Chat"),
           ("slack", "Slack"),
           ("slack", "Slack - Workspaces"),

           # Office apps
           ("word", "Microsoft Word"),
           ("word", "Document1.docx - Microsoft Word"),
           ("excel", "Microsoft Excel"),
           ("powerpoint", "Microsoft PowerPoint"),
       ]
       return test_data
   ```

4. **Implement performance benchmarking**
   ```python
   class PerformanceBenchmark:
       def __init__(self):
           self.iterations = 1000
           self.test_data = generate_real_world_test_data()

       def run_benchmark(self, matcher):
           start_time = time.time()
           matches = 0

           for i in range(self.iterations):
               for query, title in self.test_data:
                   if matcher.fuzzy_match(title, [query], 85):
                       matches += 1

           end_time = time.time()
           total_time = end_time - start_time
           matches_per_second = (matches * self.iterations) / total_time

           return {
               'total_time': total_time,
               'matches_per_second': matches_per_second,
               'total_matches': matches
           }
   ```

5. **Add threshold calibration UI**
   ```python
   class ThresholdCalibrationUI:
       def __init__(self):
           self.optimizer = ThresholdOptimizer()
           self.test_suite = FuzzyMatcherTestSuite()

       def run_calibration_dialog(self):
           # Show calibration dialog to users
           # Allow users to adjust threshold and see results
           pass

       def get_user_feedback(self, threshold, results):
           # Collect user feedback on threshold settings
           pass
   ```

6. **Final threshold integration**
   ```python
   def finalize_threshold(self, optimized_threshold):
       # Apply optimized threshold to production system
       self.fuzz_threshold = optimized_threshold
       self.save_threshold_config()
       self.reset_caches()
   ```

## Todo List
- [ ] Create threshold calibration system
- [ ] Build comprehensive test suite
- [ ] Generate real-world test data
- [ ] Implement performance benchmarking
- [ ] Add threshold calibration UI
- [ ] Run calibration tests
- [ ] Collect user feedback
- [ ] Finalize threshold integration

## Success Criteria
- ✅ Optimal threshold identified (recommended 85-90)
- ✅ Test suite passing with 95%+ accuracy
- ✅ Performance maintained at 1000+ matches per second
- ✅ Real-world scenarios tested and working
- ✅ User feedback collected and integrated
- ✅ Threshold configuration persisted

## Risk Assessment
- **High**: Suboptimal threshold affecting user experience - Mitigation: Extensive testing
- **Medium**: Test data not representative - Mitigation: Collect real-world data
- **Medium**: Performance impact of testing - Mitigation: Isolated test environment

## Security Considerations
- No security risks identified
- Threshold calibration is configuration change

## Next Steps
- Complete Phase 06 implementation
- Project completion and documentation