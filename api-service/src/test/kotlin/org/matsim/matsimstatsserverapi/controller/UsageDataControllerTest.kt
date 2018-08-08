package org.matsim.matsimstatsserverapi.controller

import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.matsim.matsimstatsserverapi.MongoTestRule
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
    @get:Rule @set:Autowired
    lateinit var mongoRule: MongoTestRule

    @Autowired
    lateinit var mvc: MockMvc

    @Test
    fun testPost() {
        mvc.perform(
                MockMvcRequestBuilders
                        .post("/api/data")
                        .contentType("application/json")
                        .content("{\"scenario\": {\"nLinks\": 1}}"))
                .andExpect(MockMvcResultMatchers.status().isOk)
        // TODO: test that data is in DB
    }
}