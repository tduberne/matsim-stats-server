package org.matsim.matsimstatsserverapi

import com.github.fakemongo.Fongo
import com.github.fakemongo.junit.FongoRule
import com.mongodb.MongoClient
import org.matsim.matsimstatsserverapi.repository.StatsRepository
import org.matsim.usagestats.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.TestConfiguration
import org.springframework.context.annotation.Configuration
import org.springframework.core.env.Environment
import org.springframework.data.mongodb.config.AbstractMongoConfiguration
import org.springframework.stereotype.Component

/**
 * @author thibautd
 */
@Configuration
class TestMongoConfiguration : AbstractMongoConfiguration() {
    @Autowired
    lateinit var env: Environment

    override fun getDatabaseName() = env.getProperty("mongo.db.name", "test")

    override fun mongoClient(): MongoClient {
        log.info("Instantiating Fongo with name $databaseName.")
        return Fongo(databaseName).mongo
    }

    companion object {
        val log: Logger = LoggerFactory.getLogger(TestConfiguration::class.java)
    }
}

@Component
class MongoTestRule  @Autowired constructor(val statsRepository: StatsRepository) : FongoRule() {
    var initializeData: Boolean = true

    override fun before() {
        // inits DB
        super.before()

        if (initializeData) {
            // add a few entries
            statsRepository.save(
                    UsageStats(
                            MemoryData(120.0, 42.0),
                            ScenarioData(1, 2, 3, 4, 5, 6),
                            MachineData("xunil", "amd124", "42", "Moon", "42"),
                            MatsimRunData("2.0", emptyList(), true)
                    )
            )
        }
    }

    // no need to take care of clearing database: FongoRule takes care of it after test
}