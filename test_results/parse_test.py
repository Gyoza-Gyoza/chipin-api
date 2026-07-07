import xml.etree.ElementTree as et
import os

tree = et.parse("test_results.xml")
root = tree.getroot()
testsuite = root.find("testsuite")
testcases = testsuite.findall("testcase")

test_count = int(testsuite.attrib['tests'])
test_errors = int(testsuite.attrib['errors'])
test_failures = int(testsuite.attrib['failures'])
test_skipped = int(testsuite.attrib['skipped'])
test_successes = test_count - test_errors - test_failures - test_skipped

failed_tests = []
for testcase in testcases:
    for result in ("error", "failure", "skipped"):
        outcome = testcase.find(result)
        if testcase.find(result) is not None:
            failed_tests.append(testcase.attrib['name'])

with open(os.environ["GITHUB_OUTPUT"], "a") as env:
    env.write(f"test_count={test_count}\n")
    env.write(f"test_successes={test_successes}\n")
    env.write(f"test_errors={test_errors}\n")
    env.write(f"test_failures={test_failures}\n")
    env.write(f"test_skipped={test_skipped}\n")
    env.write(f"failed_tests={failed_tests}\n")

