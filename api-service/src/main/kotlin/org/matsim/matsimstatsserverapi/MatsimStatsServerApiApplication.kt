package org.matsim.matsimstatsserverapi

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.autoconfigure.domain.EntityScan
import org.springframework.boot.runApplication
import org.springframework.data.jpa.repository.config.EnableJpaRepositories

@SpringBootApplication
@EntityScan(basePackages = ["org.matsim.usagestats", "org.matsim.matsimstatsserverapi"])
@EnableJpaRepositories
class MatsimStatsServerApiApplication

fun main(args: Array<String>) {
    runApplication<MatsimStatsServerApiApplication>(*args)
}
