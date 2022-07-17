# stage1 as builder
FROM node:14.15.4 as builder

WORKDIR /vue-ui

# Copy the package.json and install dependencies
COPY ./frontend/package*.json ./
COPY ./frontend/yarn.lock ./
RUN yarn install

# Copy rest of the files
COPY ./frontend .

# Build the project
RUN yarn run build

FROM nginx:alpine as production-build
COPY ./frontend/.nginx/nginx.conf /etc/nginx/nginx.conf

## Remove default nginx index page
RUN rm -rf /usr/share/nginx/html/*

# Copy from the stahg 1
COPY --from=builder /vue-ui/dist /usr/share/nginx/html

EXPOSE 80
ENTRYPOINT ["nginx", "-g", "daemon off;"]
