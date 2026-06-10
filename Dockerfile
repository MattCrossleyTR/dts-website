FROM debian:12
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm

COPY frontend /frontend/
RUN chmod -R 755 /frontend/
COPY backend /backend/
RUN chmod -R 755 /backend/

WORKDIR /frontend
RUN npm install && npm run build
WORKDIR /backend
RUN python3 -m venv ../.venv && \
    . ../.venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

COPY run.sh /run.sh

EXPOSE 3000
EXPOSE 8000

WORKDIR /
ENTRYPOINT ["bash"]
CMD ["/run.sh"]
