FROM python:3.12-slim

# python:3.12-slim ships neither `make` nor `rsync` -- both are needed to run the SAME
# package-data step `make package` uses locally (see Makefile), reused here rather than
# re-implementing its rsync excludes a second time.
RUN apt-get update && apt-get install -y --no-install-recommends make rsync \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy repo and prepare package data
COPY . .
RUN make package-data

# Install the package
RUN pip install --no-cache-dir .

# Set the default command to the CLI
ENTRYPOINT ["probity-bench"]
