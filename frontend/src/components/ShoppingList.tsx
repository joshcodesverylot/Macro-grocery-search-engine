import type { ShoppingItem } from "../types";

interface Props {
  items: ShoppingItem[];
}

export default function ShoppingList({ items }: Props) {
  return (
    <section className="panel result-panel glass">
      <header className="panel-header">
        <p className="eyebrow">Buy</p>
        <h2>Shopping list</h2>
      </header>
      <ul className="shop-list">
        {items.map((item) => (
          <li key={item.product_id} className="shop-row glass-control">
            <div>
              <strong>
                {item.packs}× {item.brand} {item.product_name}
              </strong>
              <span className="muted">
                {item.size_g} g pack · ${item.pack_price_aud.toFixed(2)} each
              </span>
            </div>
            <span className="pack-total">${(item.packs * item.pack_price_aud).toFixed(2)}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
