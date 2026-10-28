import { useEffect, useRef, useState } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Lenis from 'lenis'
import 'lenis/dist/lenis.css'
import ProductSequence from './ProductSequence'
import sequence from './sequenceManifest.json'
gsap.registerPlugin(ScrollTrigger)
export default function App() {
  const lenisRef=useRef(null), dialog=useRef(null)
  const [bagQuantity,setBagQuantity]=useState(()=>{
    const quantity=Number(localStorage.getItem('lumora-hair-oil-bag'))
    return Number.isSafeInteger(quantity) && quantity>0 ? quantity : 0
  })
  useEffect(()=>{
    if(matchMedia('(prefers-reduced-motion: reduce)').matches) return
    const lenis=new Lenis({lerp:.12,smoothWheel:true,syncTouch:false}); lenisRef.current=lenis
    lenis.on('scroll',ScrollTrigger.update)
    const tick=time=>lenis.raf(time*1000); gsap.ticker.add(tick)
    return ()=>{gsap.ticker.remove(tick);lenis.destroy();lenisRef.current=null}
  },[])
  const navigate=event=>{
    const href=event.target.closest('a')?.getAttribute('href')
    if(!href?.startsWith('#') || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
    const target=document.getElementById(href.slice(1)); if(!target) return
    event.preventDefault()
    const complete=()=>{history.replaceState(null,'',href);target.focus({preventScroll:true})}
    if(lenisRef.current) lenisRef.current.scrollTo(target,{duration:1.1,onComplete:complete})
    else {target.scrollIntoView();complete()}
  }
  const openCart=()=>{dialog.current.showModal();lenisRef.current?.stop()}
  const updateBagQuantity=quantity=>{
    const next=Math.max(0,quantity)
    localStorage.setItem('lumora-hair-oil-bag',String(next))
    setBagQuantity(next)
  }
  const addToBag=()=>updateBagQuantity(bagQuantity+1)
  return <div onClick={navigate}>
    <a className="skip-link" href="#shop">Skip animation</a>
    <header className="site-header"><a className="wordmark" href="#top" aria-label="Dr. Yogitha's home">Dr. Yogitha's</a><nav aria-label="Main navigation"><a href="#formula">The formula</a><a href="#craft">The craft</a><a href="#result">The ritual</a></nav><button className="bag-button" aria-label={`View shopping bag, ${bagQuantity} items`} onClick={openCart}><svg width="17" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true"><path d="M5 8h14l1 13H4L5 8Z"/><path d="M9 9V6a3 3 0 0 1 6 0v3"/></svg><span aria-hidden="true">{bagQuantity}</span></button><a href="#shop" className="nav-shop">Shop</a></header>
    <main><ProductSequence/>
      <section id="shop" className="shop-section" tabIndex={-1}><div className="shop-image"><img src={`${import.meta.env.BASE_URL}${sequence.directory}/product.webp?v=${sequence.revision}`} alt="Ayurvedic hair oil in a clear bottle with a black cap and cream botanical label, on a sunlit table in a lush garden" width="1920" height="1080" loading="lazy"/><span>DR. YOGITHA'S / AYURVEDIC HAIR OIL</span></div><div className="shop-copy"><p className="eyebrow">THE COLLECTION</p><h2>Ayurvedic <span>Hair Oil</span></h2><p className="shop-description">Rooted in a botanical tradition.<br/>Make a little time for your hair.</p><div className="shop-price"><strong>Coming soon</strong><span>Price and launch details to be announced</span></div><dl className="product-details"><div><dt>KEY INGREDIENTS</dt><dd>Botanical oils inspired by Ayurvedic traditions</dd></div><div><dt>TEXTURE</dt><dd>A golden oil for a considered hair-care ritual</dd></div><div><dt>USE</dt><dd>Make a little time for your hair, your way</dd></div><div><dt>BOTTLE</dt><dd>Clear bottle with a black cap and botanical label</dd></div></dl><button className="shop-button" onClick={addToBag}><svg width="17" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="M5 8h14l1 13H4L5 8Z"/><path d="M9 9V6a3 3 0 0 1 6 0v3"/></svg><span>Add to bag</span></button></div></section>
      <section id="routine" className="routine" tabIndex={-1}><div className="routine-heading"><p className="eyebrow">DR. YOGITHA'S AYURVEDIC HAIR OIL</p><h2>A ritual rooted in care.</h2></div><div className="routine-grid"><article><span>01</span><h3>Botanical by tradition</h3><p>Hair oil inspired by Ayurvedic botanical care.</p></article><article><span>02</span><h3>Golden oil, considered care</h3><p>A simple way to make time for your hair.</p></article><article><span>03</span><h3>Your hair ritual</h3><p>Bring a little intention to your hair-care routine.</p></article></div></section>
    </main>
    <footer><div className="footer-grid"><div><a className="wordmark" href="#top">Dr. Yogitha's</a><p>Ayurvedic hair oil inspired by botanical traditions.<br/>A mindful ritual for your hair.</p></div><div><h3>SHOP</h3><a href="#shop">Ayurvedic Hair Oil</a></div><div><h3>DISCOVER</h3><a href="#formula">The ingredients</a><a href="#craft">The making</a><a href="#routine">Your hair ritual</a></div><div><h3>THE STUDIO</h3><p>A botanical approach to hair care.<br/>Made for a mindful daily ritual.</p></div></div><div className="footer-bottom"><span>© {new Date().getFullYear()} Dr. Yogitha's</span><span>Ayurvedic Hair Oil</span><a href="#top">Back to top ↑</a></div></footer>
    <dialog className="cart-dialog" ref={dialog} onClose={()=>lenisRef.current?.start()} onClick={event=>{if(event.target===dialog.current) dialog.current.close()}}><div className="cart-header"><h2>Your bag <span>{bagQuantity} {bagQuantity===1 ? 'item' : 'items'}</span></h2><button className="dialog-close" onClick={()=>dialog.current.close()} aria-label="Close shopping bag">×</button></div><div className="cart-content">{bagQuantity===0 ? <p className="cart-empty">Your bag is empty.</p> : <div className="cart-item"><img src={`${import.meta.env.BASE_URL}${sequence.directory}/product.webp?v=${sequence.revision}`} alt="" width="1920" height="1080"/><div className="cart-item-copy"><h3>Ayurvedic Hair Oil</h3><p>Botanical hair oil</p><div className="cart-quantity"><button aria-label="Remove one hair oil from bag" onClick={()=>updateBagQuantity(bagQuantity-1)}>−</button><span aria-live="polite">{bagQuantity}</span><button aria-label="Add one hair oil to bag" onClick={()=>updateBagQuantity(bagQuantity+1)}>+</button></div></div><div className="cart-item-price"><strong>Price at launch</strong><button className="cart-remove" onClick={()=>updateBagQuantity(0)}>Remove</button></div></div>}</div><div className="cart-footer">{bagQuantity>0 ? <><div className="cart-summary-row"><span>Subtotal</span><span>To be announced</span></div><div className="cart-summary-row"><span>Delivery</span><span>At launch</span></div><button className="shop-button cart-checkout" disabled>Checkout <span aria-hidden="true">→</span></button><small>Checkout will be available when the product launches.</small></> : <button className="shop-button cart-checkout" onClick={()=>dialog.current.close()}>Continue browsing</button>}</div></dialog>
  </div>
}
