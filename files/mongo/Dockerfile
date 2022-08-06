FROM mongo:5.0.10-focal

ENV MONGO_INITDB_ROOT_USERNAME=root
ENV MONGO_INITDB_ROOT_PASSWORD=passowrd
ENV MONGO_INITDB_DATABASE=user_prediction

# COPY mongod.conf /etc/mongod.conf
COPY init.js /docker-entrypoint-initdb.d/