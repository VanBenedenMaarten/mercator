FROM node:lts-alpine@sha256:b375b98d1dcd56f5783efdd80a4d6ff5a0d6f3ce7921ec99c17851db6cba2a93

RUN apk add -u --no-cache \
    libstdc++ \
    chromium \
    harfbuzz \
    nss \
    freetype \
    ttf-freefont \
    font-noto-emoji

RUN \
    # CVE-2022-30065 \
    apk upgrade --no-cache busybox && \
    # CVE-2022-37434 \
    apk upgrade --no-cache zlib && \
    # CVE-2023-24056
    apk upgrade --no-cache pkgconf && \
    # CVE-2023-0286
    apk upgrade --no-cache libssl3 libcrypto3

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser \
    CHROME_BIN=/usr/bin/chromium-browser \
    CHROME_PATH=/usr/lib/chromium/

#ARG NODE_ENV=production
#ENV NODE_ENV $NODE_ENV

WORKDIR /app
RUN chown node:node ./
USER node

ADD package.json package-lock.json /app/

RUN npm ci && npm cache clean --force

ADD tsconfig.json /app
ADD src /app/src
ADD .env /app/.env

# RUN npm run build --omit=dev
RUN npm run build

CMD ["node", "/app/dist/index.js"]
