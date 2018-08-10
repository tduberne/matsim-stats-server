package org.matsim.matsimstatsserverapi.controller

import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.matsim.matsimstatsserverapi.service.StatsService
import org.matsim.usagestats.ScenarioData
import org.matsim.usagestats.UsageStats
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.test.context.junit4.SpringRunner
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders
import org.springframework.test.web.servlet.result.MockMvcResultMatchers

/**
 * @author thibautd
 */
@RunWith(SpringRunner::class)
@SpringBootTest
@AutoConfigureMockMvc
class UsageDataControllerTest {

    @Autowired
    lateinit var mvc: MockMvc

    @Autowired
    lateinit var statsService: StatsService

    @Test
    fun testPost() {
        mvc.perform(
                MockMvcRequestBuilders
                        .post("/api/data")
                        .contentType("application/json")
                        .content("{\"scenario\": {\"nLinks\": 42}}"))
                .andExpect(MockMvcResultMatchers.status().isOk)

        Assert.assertEquals("unexpected number of entries", 1, statsService.allEntries().size)
        Assert.assertEquals("unexpected data",
                UsageStats(scenario = ScenarioData(nLinks = 42)),
                statsService.allEntries()[0])
    }
}