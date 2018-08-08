###########################################################################
# BUILD
###########################################################################
FROM maven:3-jdk-8 as builder

RUN mkdir /app

WORKDIR /app

# First only add pom and update dependencies. This will allow Docker to use
# cache if pom did not change.
COPY pom.xml ./
RUN mvn -B verify clean --fail-never

# Then, and only then, build the rest
COPY . ./
RUN mvn -B clean package


###########################################################################
# PACKAGE (without maven)
###########################################################################
FROM openjdk:alpine as runner
RUN mkdir /app
WORKDIR /app
COPY --from=builder /app/target/*.jar ./

# TODO: see if possible to get from application.properties
EXPOSE 8000

CMD java -jar /app/*.jar
