FROM python:3.11-slim
WORKDIR /app
# Install the package itself
COPY . .
RUN pip install --no-cache-dir -e . pymodbus click
ENTRYPOINT ["modbus-log"]
