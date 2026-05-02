# Step 1: Use an official Python runtime as a parent image
# The "slim" tag means it's a smaller, stripped-down version of Linux, which makes our final image smaller.
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
# Imagine this as creating a folder inside the Docker computer and 'cd'ing into it.
WORKDIR /app

# Step 3: Copy the requirements file into the container
# We do this first before copying the rest of the code to take advantage of Docker caching.
COPY requirements.txt .

# Step 4: Install any needed packages specified in requirements.txt
# This command runs inside the container during the build process.
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of your application's code into the container
# The first '.' is your computer's current folder, the second '.' is the container's working directory (/app).
COPY . .

# Step 6: Expose the port that the app will run on
# This tells Docker that the container listens on port 8000 at runtime.
EXPOSE 8000

# Step 7: Define the command to run your application
# This is what executes when the container actually starts.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
