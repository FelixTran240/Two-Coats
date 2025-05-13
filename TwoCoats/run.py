import os
import sys
from gunicorn.app.wsgiapp import run

# Set defualt port if not set
os.environ.setdefault("PORT", "8000")

# Set the target for Gunicorn
sys.argv += ["TwoCoats.src.app:app", "--bind", f"0.0.0.0:{os.environ['PORT']}"]

run()

