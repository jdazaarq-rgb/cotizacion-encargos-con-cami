package com.personalshopper.app.service;

import com.personalshopper.app.model.Category;
import com.personalshopper.app.model.QuoteItem;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.assertEquals;

class PricingServiceTest {
    private final PricingService service = new PricingService();
    private final Category tenis = new Category("Tenis", new BigDecimal("0.40"), new BigDecimal("150000"));

    @Test
    void appliesSevenPercentTaxAndRoundsToTenThousand() {
        QuoteItem item = service.calculate("Tenis prueba", tenis,
                new BigDecimal("60"), new BigDecimal("3200"));

        assertEquals(new BigDecimal("4.20"), item.taxUsd());
        assertEquals(new BigDecimal("205440.00"), item.costCop());
        assertEquals(new BigDecimal("360000"), item.customerPriceCop());
        assertEquals(new BigDecimal("154560.00"), item.profitCop());
        assertEquals("GANANCIA", item.status());
    }
}
