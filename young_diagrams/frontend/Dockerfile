FROM node:18 as build

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the entire application code to the container
COPY . ./

# Build the React app for production
RUN npm run build

# Команда для копирования собранных файлов во внешний том
CMD ["sh", "-c", "cp -r dist/* /app/dist/ && tail -f /dev/null"]

