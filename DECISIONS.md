# Decisions

## The "2 kg salt" Conflict (Rule 1 vs Rule 2)

**Decision:** Rule 1 (Quantity/Measured) wins over Rule 2 (Pantry Staple). A user entering "2 kg salt" will receive a dynamic **measured** badge rather than a static **staple** badge.

**Reasoning:**
When a user explicitly types a quantity and unit, that specific measurement is the most salient piece of information for their shopping task. "2 kg salt" implies the user needs to find a specific, heavy, bulk item, which is a structurally different physical task than just grabbing a small shaker of "salt". 

By letting Rule 1 win, we retain the utility of the dynamic shade-scaling feature: heavy/large items will visually stand out on the grocery list as darker badges. If we allowed the staple rule to win, we would discard this valuable, user-provided sizing information in favor of a generic grey tag. Therefore, specific user input (measurements) should always override generic categories (staples).
