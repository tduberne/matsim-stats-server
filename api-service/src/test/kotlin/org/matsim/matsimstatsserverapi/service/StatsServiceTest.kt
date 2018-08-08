package org.matsim.matsimstatsserverapi.service

import org.junit.Assert
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.matsim.matsimstatsserverapi.MongoTestRule
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.test.context.junit4.SpringRunner

/**
 * @author thibautd
 */
@RunWith(SpringRunner::class)
@SpringBootTest
class StatsServiceTest {
    @get:Rule @set:Autowired
    lateinit var mongoRule: MongoTestRule

    @Autowired
    lateinit var statsService : StatsService

    @Test
    fun testEntriesExist() {
        Assert.assertEquals(1, statsService.allEntries().size)
    }
}
