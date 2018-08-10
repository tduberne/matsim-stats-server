package org.matsim.matsimstatsserverapi

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.autoconfigure.domain.EntityScan
import org.springframework.boot.runApplication
import org.springframework.data.jpa.repository.config.EnableJpaRepositories

@SpringBootApplication
@EntityScan("org.matsim.usagestats")
@EnableJpaRepositories
class MatsimStatsServerApiApplication

fun main(args: Array<String>) {
    runApplication<MatsimStatsServerApiApplication>(*args)
}
