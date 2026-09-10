package com.personalshopper.app.model;

import java.math.BigDecimal;

public record QuoteItem(
        String product,
        String category,
        BigDecimal priceUsd,
        BigDecimal taxUsd,
        BigDecimal totalUsd,
        BigDecimal trm,
        BigDecimal costCop,
        BigDecimal customerPriceCop,
        BigDecimal profitCop,
        String status) {
}
