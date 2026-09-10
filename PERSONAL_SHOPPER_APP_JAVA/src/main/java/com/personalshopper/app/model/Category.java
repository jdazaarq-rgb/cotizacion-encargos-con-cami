package com.personalshopper.app.model;

import java.math.BigDecimal;

public record Category(String name, BigDecimal surchargeRate, BigDecimal minimumProfit) {
}
