import { useEffect, useRef, useState } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Lenis from 'lenis'
import 'lenis/dist/lenis.css'
import ProductSequence from './ProductSequence'
gsap.registerPlugin(ScrollTrigger)
export default function App() {
  const lenisRef=useRef(null), dialog=useRef(null)
  const [submitted,setSubmitted]=useState(false)
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
  const openDetails=()=>{setSubmitted(localStorage.getItem('lumora-interest')==='true');dialog.current.showModal();lenisRef.current?.stop()}
  return <div onClick={navigate}>
    <a className="skip-link" href="#shop">Skip animation</a>
    <header className="site-header"><a className="wordmark" href="#top" aria-label="Lumora home">LUMORA</a><nav aria-label="Main navigation"><a href="#formula">The formula</a><a href="#spots">The skin</a><a href="#result">The ritual</a></nav><button className="bag-button" aria-label="View collection availability" onClick={openDetails}><svg width="17" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true"><path d="M5 8h14l1 13H4L5 8Z"/><path d="M9 9V6a3 3 0 0 1 6 0v3"/></svg><span>0</span></button><a href="#shop" className="nav-shop">Shop</a></header>
    <main><ProductSequence/>
      <section id="shop" className="shop-section" tabIndex={-1}><div className="shop-image"><img src={`${import.meta.env.BASE_URL}scenes/product.webp`} alt="Aurum Serum amber glass bottle with its black dropper and ivory label" width="1000" height="1100" loading="lazy"/><span>LUMORA — THE SIGNATURE SERUM</span></div><div className="shop-copy"><p className="eyebrow">THE COLLECTION</p><h2>Aurum <span>Serum</span></h2><p className="shop-description">A little more intention.<br/>A beautiful addition to your everyday ritual.</p><p className="availability"><span/> Coming soon</p><p className="shop-note">Our first chapter is taking shape. Product details and purchasing will be available at launch.</p><button className="shop-button" onClick={openDetails}>Explore the collection <span aria-hidden="true">↗</span></button><div className="shop-meta"><span>Amber glass</span><span>Thoughtfully considered</span><span>A daily ritual</span></div></div></section>
      <section id="routine" className="routine" tabIndex={-1}><div className="routine-heading"><p className="eyebrow">MAKE TIME FOR YOURSELF</p><h2>A simpler kind of ritual.</h2></div><div className="routine-grid"><article><span>01</span><h3>Slow down</h3><p>A quiet pause in an otherwise busy day.</p></article><article><span>02</span><h3>Make it yours</h3><p>A considered addition to your daily routine.</p></article><article><span>03</span><h3>Come back to you</h3><p>Small moments. A little more intention.</p></article></div></section>
    </main>
    <footer><div className="footer-grid"><div><a className="wordmark" href="#top">LUMORA</a><p>One serum. A beautiful object.<br/>A moment that belongs to you.</p></div><div><h3>SHOP</h3><a href="#shop">Aurum Serum</a></div><div><h3>DISCOVER</h3><a href="#formula">The formula</a><a href="#spots">The skin</a><a href="#routine">The ritual</a></div><div><h3>THE STUDIO</h3><p>Thoughtfully crafted.<br/>Beautifully simple.</p></div></div><div className="footer-bottom"><span>© {new Date().getFullYear()} Lumora</span><span>Concept collection</span><a href="#top">Back to top ↑</a></div></footer>
    <dialog ref={dialog} onClose={()=>lenisRef.current?.start()} onClick={event=>{if(event.target===dialog.current) dialog.current.close()}}><button className="dialog-close" onClick={()=>dialog.current.close()} aria-label="Close collection details">×</button><p className="eyebrow">LUMORA / AURUM</p><h2>A new daily ritual.</h2><p>{submitted ? 'Your interest is saved on this device. Come back here for launch updates.' : 'Aurum Serum is in development. Purchasing and the full product details will be available at launch.'}</p><button className="shop-button" onClick={()=>{localStorage.setItem('lumora-interest','true');setSubmitted(true)}} disabled={submitted}>{submitted ? 'Interest saved ✓' : 'Save my interest on this device'}</button><small>This saves a preference in your browser. No email is collected.</small></dialog>
  </div>
}
