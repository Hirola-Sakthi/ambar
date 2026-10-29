import { forwardRef } from "react";
import sequence from "../sequenceManifest.json";

const BagDialog = forwardRef(function BagDialog(
  { bagQuantity, lenisRef, updateBagQuantity },
  dialog,
) {
  return (
    <dialog
      className="cart-dialog"
      ref={dialog}
      onClose={() => lenisRef.current?.start()}
      onClick={(event) => {
        if (event.target === dialog.current) dialog.current.close();
      }}
    >
      <div className="cart-header">
        <h2>
          Your bag{" "}
          <span>
            {bagQuantity} {bagQuantity === 1 ? "item" : "items"}
          </span>
        </h2>
        <button
          className="dialog-close"
          onClick={() => dialog.current.close()}
          aria-label="Close shopping bag"
        >
          ×
        </button>
      </div>
      <div className="cart-content">
        {bagQuantity === 0 ? (
          <p className="cart-empty">Your bag is empty.</p>
        ) : (
          <div className="cart-item">
            <img
              src={`${import.meta.env.BASE_URL}${sequence.directory}/product.webp?v=${sequence.revision}`}
              alt=""
              width="1920"
              height="1080"
            />
            <div className="cart-item-copy">
              <h3>Ayurvedic Hair Oil</h3>
              <p>Botanical hair oil</p>
              <div className="cart-quantity">
                <button
                  aria-label="Remove one hair oil from bag"
                  onClick={() => updateBagQuantity(bagQuantity - 1)}
                >
                  −
                </button>
                <span aria-live="polite">{bagQuantity}</span>
                <button
                  aria-label="Add one hair oil to bag"
                  onClick={() => updateBagQuantity(bagQuantity + 1)}
                >
                  +
                </button>
              </div>
            </div>
            <div className="cart-item-price">
              <strong>Price at launch</strong>
              <button
                className="cart-remove"
                onClick={() => updateBagQuantity(0)}
              >
                Remove
              </button>
            </div>
          </div>
        )}
      </div>
      <div className="cart-footer">
        {bagQuantity > 0 ? (
          <>
            <div className="cart-summary-row">
              <span>Subtotal</span>
              <span>To be announced</span>
            </div>
            <div className="cart-summary-row">
              <span>Delivery</span>
              <span>At launch</span>
            </div>
            <button className="shop-button cart-checkout" disabled>
              Checkout <span aria-hidden="true">→</span>
            </button>
            <small>Checkout will be available when the product launches.</small>
          </>
        ) : (
          <button
            className="shop-button cart-checkout"
            onClick={() => dialog.current.close()}
          >
            Continue browsing
          </button>
        )}
      </div>
    </dialog>
  );
});

export default BagDialog;
