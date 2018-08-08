###########################################################################
# BUILD
###########################################################################
FROM maven:3-jdk-8

RUN mkdir /app

WORKDIR /app

# First only add pom and update dependencies. This will allow Docker to use
# cache if pom did not change.
ADD pom.xml ./
RUN mvn -B verify clean --fail-never

# Then, and only then, build the rest
ADD . ./
RUN mvn -B clean package


###########################################################################
# PACKAGE (without maven)
###########################################################################
FROM openjdk:alpine
COPY --from=0 /app/target/*.jar ./

# TODO: see if possible to get from application.properties
EXPOSE 8000

CMD ["java", "-jar", "/app/target/*.jar"]
