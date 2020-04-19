FROM base_docker

WORKDIR /runtime
COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT python3 runtime.py
