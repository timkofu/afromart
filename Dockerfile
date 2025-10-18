# Globals
ARG PYTHON_VERSION=3.14.0


### Build image ###
FROM debian:trixie as build

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 LC_ALL=C.UTF-8

ARG PYTHON_VERSION
ARG LLVM_VERSION=21

# Add LLVM repository
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes curl ca-certificates gnupg && \
    update-ca-certificates && \
    curl -fsSL https://apt.llvm.org/llvm-snapshot.gpg.key | gpg --dearmor -o /usr/share/keyrings/llvm-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/llvm-archive-keyring.gpg] http://apt.llvm.org/trixie/ llvm-toolchain-trixie-${LLVM_VERSION} main" > /etc/apt/sources.list.d/llvm.list

# Install build dependencies
ARG PYTHON_BUILD_DEPS="libc6-dev libstdc++-14-dev zlib1g-dev libncurses-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev liblzma-dev tk-dev"
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    # For JIT: llvm-19 clang-19 lld-19 libclang-rt-19-dev \
    llvm-${LLVM_VERSION} clang-${LLVM_VERSION} lld-${LLVM_VERSION} \
    libclang-rt-${LLVM_VERSION}-dev \
    ${PYTHON_BUILD_DEPS:-}
RUN ln -sf /usr/bin/llvm-ar-${LLVM_VERSION} /usr/local/bin/llvm-ar && \
    ln -sf /usr/bin/llvm-ranlib-${LLVM_VERSION} /usr/local/bin/llvm-ranlib && \
    ln -sf /usr/bin/llvm-profdata-${LLVM_VERSION} /usr/local/bin/llvm-profdata

# Compile Python
ENV CC=clang-${LLVM_VERSION} \
    CXX=clang++-${LLVM_VERSION} \
    CFLAGS="-march=native -O3 -flto -pipe" \
    LDFLAGS="-fuse-ld=lld-${LLVM_VERSION}" \
    CXXFLAGS="-march=native -O3 -flto -pipe"
RUN set -eux; mkdir /python-build && cd /python-build && \
    curl -O https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar xzf Python-${PYTHON_VERSION}.tgz --strip-components=1 && \
    ./configure --enable-optimizations --with-lto=full \
      --disable-test-modules --disable-gil \
      --with-tail-call-interp --prefix=/opt/python && \
    make -j$(nproc) && \
    make install -j$(nproc)
RUN /usr/bin/strip /opt/python/bin/python${PYTHON_VERSION%.*} || true
RUN rm -rf /python-build && \
    apt-get purge --auto-remove --yes curl ca-certificates gnupg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project over
COPY . .

# Install Python dependencies
ENV PATH="/opt/python/bin:$PATH"
RUN python${PYTHON_VERSION%.*} -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir --requirement requirements.pip

    
### Production image ###
FROM debian:trixie-slim

LABEL maintainer="Timothy Makobu <timothy@makobu.name>"

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PRODUCTION=1
    
# Install runtime dependencies
ARG PYTHON_RUNTIME_DEPS="zlib1g libncursesw6 libgdbm6t64 libnss3 libssl3t64 libreadline8t64 libffi8 libsqlite3-0 libbz2-1.0 liblzma5 libtcl8.6 libtk8.6 libpq5"
RUN apt-get update && \
    apt-get install --yes curl ca-certificates gnupg && \
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt trixie-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update && \
    apt-get install --no-install-recommends --yes ${PYTHON_RUNTIME_DEPS:-} && \
    apt-get purge --auto-remove --yes curl ca-certificates gnupg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Python
COPY --from=build /opt/python /opt/python
ENV PATH="/opt/python/bin:$PATH"

# Set work directory
WORKDIR /app

# Copy Python dependencies
COPY --from=build /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy project to container
COPY afromart .

# Copy static files
RUN python manage.py collectstatic --noinput --clear

# Add and run as non-root user
RUN groupadd -g 53556 afromart && \
    useradd -u 53556 -g 53556 -ms /bin/bash afromart && \
    chown -R afromart:afromart /app
USER afromart
