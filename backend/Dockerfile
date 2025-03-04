
FROM python:3.8

# # install cmake and git
RUN apt-get update && apt-get install -y cmake ffmpeg libsndfile1

# # clone whisper.cpp
# RUN git clone https://github.com/ggerganov/whisper.cpp.git /app/whisper

# # Build whisper-cli
# WORKDIR /app/whisper

# RUN cmake -B build 
# RUN cmake --build build --config Release
WORKDIR /app
COPY ./conan-profile .
RUN pip install conan
RUN conan profile detect
RUN conan install --requires="whisper-cpp/[*]" --profile:build=conan-profile --build=missing



# Copy local whisper-cli binary and other required files
COPY . /app/

RUN pip install -r requirements.txt


CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# docker run -v /Volumes/Other/whisper/:/models -p 8000:8000 whisper-api
