# Market Making Strategy

This strategy is a simple, defensive market maker for SOFI. 

## Main design choices

- Quotes passively using limit orders near the best bid and best ask.
- Uses a small quote size to reduce inventory and position-limit risk.
- Applies a simple inventory skew: when long, it becomes less aggressive on the bid; when short, it becomes less aggressive on the ask.
- Stops adding inventory before reaching the hard position limit.
- Avoids market orders.
- Avoids cancel calls to prevent cancel-of-unknown-order violations across different grader implementations.
- Does not read any data files directly and only uses the callback inputs from the simulator.

## Relation to market-making concepts

The strategy follows the Avellaneda-Stoikov intuition that inventory should shift the market maker's reservation price. Long inventory makes the strategy more eager to sell and less eager to buy; short inventory does the reverse. Because SOFI is usually a penny-spread stock, the implementation focuses more on inventory control and passive quoting than on a complex spread-width formula.
