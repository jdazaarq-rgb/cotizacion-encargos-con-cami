package com.personalshopper.app.service;

import com.personalshopper.app.model.Category;
import com.personalshopper.app.model.QuoteItem;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;

@Service
public class PricingService {
    private static final BigDecimal TAX_RATE = new BigDecimal("0.07");
    private static final BigDecimal ROUNDING_UNIT = new BigDecimal("10000");

    public QuoteItem calculate(String product, Category category, BigDecimal priceUsd, BigDecimal trm) {
        if (product == null || product.isBlank()) {
            throw new IllegalArgumentException("El producto es obligatorio.");
        }
        if (priceUsd == null || priceUsd.signum() <= 0) {
            throw new IllegalArgumentException("El precio en USD debe ser mayor que cero.");
        }
        if (trm == null || trm.signum() <= 0) {
            throw new IllegalArgumentException("La TRM debe ser mayor que cero.");
        }

        BigDecimal taxUsd = priceUsd.multiply(TAX_RATE);
        BigDecimal totalUsd = priceUsd.add(taxUsd);
        BigDecimal costCop = totalUsd.multiply(trm);
        BigDecimal byRate = costCop.multiply(BigDecimal.ONE.add(category.surchargeRate()));
        BigDecimal byMinimum = costCop.add(category.minimumProfit());
        BigDecimal customerPrice = roundUpTo10000(byRate.max(byMinimum));
        BigDecimal profit = customerPrice.subtract(costCop);
        String status = profit.signum() < 0
                ? "PERDIDA"
                : profit.compareTo(category.minimumProfit()) < 0 ? "REVISAR" : "GANANCIA";

        return new QuoteItem(product.trim(), category.name(), priceUsd, taxUsd, totalUsd, trm,
                costCop, customerPrice, profit, status);
    }

    public BigDecimal roundUpTo10000(BigDecimal value) {
        return value.divide(ROUNDING_UNIT, 0, RoundingMode.CEILING).multiply(ROUNDING_UNIT);
    }
}
