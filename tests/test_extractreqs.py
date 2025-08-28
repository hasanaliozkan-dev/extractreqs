
import os
import tempfile
import extractreqs

def test_extractreq_basic():
	code = """
import sys
import requests
import numpy as np
import skimage
import sklearn
"""
	with tempfile.TemporaryDirectory() as tmpdir:
		test_file = os.path.join(tmpdir, "test.py")
		with open(test_file, "w") as f:
			f.write(code)
		reqs = extractreqs.extractreq(tmpdir)
		# Should find at least requests, numpy, scikit-image, scikit-learn
		assert any("requests" in r for r in reqs)
		assert any("numpy" in r for r in reqs)
		assert any("scikit-image" in r for r in reqs)
		assert any("scikit-learn" in r for r in reqs)
