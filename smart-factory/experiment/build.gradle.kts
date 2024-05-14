plugins {
    application
    id("java")
    id("org.graalvm.buildtools.native") version "0.10.1"
}

group = "at.ac.uibk.dps.smartfactory"
version = "1.0-SNAPSHOT"

graalvmNative {
    binaries {
        named("main") {
            imageName.set("cirrina_smartfactory")
            mainClass.set("ac.at.uibk.dps.smartfactory.TestLocal")
            buildArgs.add("-O4")
        }
        named("test") {
            buildArgs.add("-O0")
        }
    }
    binaries.all {
        buildArgs.add("--verbose")
    }
}

repositories {
    mavenCentral()
    maven(url = "https://repository.cloudera.com/artifactory/cloudera-repos/")
}

dependencies {

    implementation(project(":cirrina"))

    implementation("com.beust:jcommander:1.82")

    implementation("com.fasterxml.jackson.core:jackson-databind:2.15.1")
    implementation("com.fasterxml.jackson.module:jackson-module-parameter-names:2.15.1")
    implementation("com.fasterxml.jackson.module:jackson-module-jsonSchema:2.15.1")
    implementation("com.fasterxml.jackson.datatype:jackson-datatype-jdk8:2.15.1")
    implementation("com.fasterxml.jackson.datatype:jackson-datatype-jsr310:2.15.1")

    implementation("com.google.guava:guava:33.0.0-jre")

    implementation(platform("io.opentelemetry:opentelemetry-bom:1.37.0"));
    implementation("io.opentelemetry:opentelemetry-api");
    implementation("io.opentelemetry:opentelemetry-sdk");
    implementation("io.opentelemetry:opentelemetry-exporter-logging");
    implementation("io.opentelemetry:opentelemetry-exporter-otlp");
    implementation("io.opentelemetry.semconv:opentelemetry-semconv:1.25.0-alpha");
    implementation("io.opentelemetry:opentelemetry-sdk-extension-autoconfigure");

    implementation("jakarta.annotation:jakarta.annotation-api:3.0.0")

    implementation("org.apache.logging.log4j:log4j-core:2.23.1")

    implementation("org.apache.zookeeper:zookeeper-client:3.8.1.7.1.9.0-387")

    implementation("org.furyio:fury-core:0.4.1")

    implementation("org.hibernate.validator:hibernate-validator:8.0.1.Final")
    implementation("org.hibernate:hibernate-validator-cdi:8.0.1.Final")

    implementation("org.jgrapht:jgrapht-core:1.5.2")
    implementation("org.jgrapht:jgrapht-io:1.5.2")

    testImplementation("org.mockito:mockito-core:5.11.0")

    testImplementation(platform("org.junit:junit-bom:5.9.1"))
    testImplementation("org.junit.jupiter:junit-jupiter")
}

tasks {

    task("runTestServer", type = JavaExec::class) {
        mainClass = "at.ac.uibk.dps.smartfactory.TestServer"
        classpath = sourceSets["main"].runtimeClasspath
    }

    task("runTestLocal", type = JavaExec::class) {
        mainClass = "at.ac.uibk.dps.smartfactory.TestLocal"
        classpath = sourceSets["main"].runtimeClasspath
    }

    task("runTestPlantUML", type = JavaExec::class) {
        mainClass = "at.ac.uibk.dps.smartfactory.TestPlantUML"
        classpath = sourceSets["main"].runtimeClasspath
    }
}
