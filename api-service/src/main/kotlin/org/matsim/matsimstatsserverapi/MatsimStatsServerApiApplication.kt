package org.matsim.matsimstatsserverapi

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class MatsimStatsServerApiApplication

fun main(args: Array<String>) {
    runApplication<MatsimStatsServerApiApplication>(*args)
}
