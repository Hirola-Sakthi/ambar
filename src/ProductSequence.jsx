import { useEffect, useRef, useState } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
gsap.registerPlugin(ScrollTrigger)
const COUNT = 240
const url = (i) => `${import.meta.env.BASE_URL}scenes/sequence/frame_${String(i + 1).padStart(4, '0')}.webp`
export default function ProductSequence() {
  const section = useRef(null), canvas = useRef(null)
  const [failed, setFailed] = useState(false)
  useEffect(() => {
    const el = canvas.current, ctx = el.getContext('2d', { alpha: false })
    if (!ctx) return
    const reduced = matchMedia('(prefers-reduced-motion: reduce)')
    const cache = new Map(), loading = new Set(), failures = new Set()
    let desired = 0, drawn = -1, raf = 0, disposed = false
    const draw = () => {
      raf = 0
      if (disposed || !cache.size) return
      const index = cache.has(desired) ? desired : [...cache.keys()].reduce((a,b) => Math.abs(a-desired) < Math.abs(b-desired) ? a : b)
      if (index === drawn) return
      const image = cache.get(index), scale = Math.max(el.width/image.width,el.height/image.height)
      ctx.drawImage(image,(el.width-image.width*scale)*(el.clientWidth<700 ? .59 : .5),(el.height-image.height*scale)/2,image.width*scale,image.height*scale)
      el.style.opacity = '1'; el.dataset.frame = String(index+1); drawn = index
    }
    const schedule = () => { if (!raf && !disposed) raf = requestAnimationFrame(draw) }
    const pump = () => {
      if (disposed) return
      const candidates = [desired]
      if (!reduced.matches) for(let o=1;o<=14;o++) candidates.push(desired+o,desired-o)
      for(const i of candidates) {
        if(loading.size>=4) break
        if(i<0 || i>=COUNT || cache.has(i) || loading.has(i) || failures.has(i)) continue
        loading.add(i)
        const image = new Image(); image.decoding='async'
        image.onload = () => {
          loading.delete(i)
          if(disposed) return
          cache.set(i,image)
          const farthest=[...cache.keys()].sort((a,b)=>Math.abs(b-desired)-Math.abs(a-desired))
          while(cache.size>40) cache.delete(farthest.shift())
          schedule(); pump()
        }
        image.onerror = () => { loading.delete(i); failures.add(i); if(!disposed) { if(failures.size>8 && !cache.size) setFailed(true); pump() } }
        image.src=url(i)
      }
    }
    const resize = () => {
      const dpr=Math.min(devicePixelRatio||1,1.5)
      el.width=Math.round(el.clientWidth*dpr); el.height=Math.round(el.clientHeight*dpr)
      drawn=-1; schedule()
    }
    const observer=new ResizeObserver(resize); observer.observe(el); resize()
    const panels=section.current.querySelectorAll('.scene-copy')
    const updatePanels = (progress) => {
      const windows=[[0,0,.105,.16],[.17,.215,.37,.415],[.49,.535,.65,.695],[.75,.795,.97,1]]
      panels.forEach((panel,index)=>{
        const [start,full,end,done]=windows[index]
        const opacity=progress<start || progress>done ? 0 : progress<full ? (progress-start)/(full-start) : progress>end ? 1-(progress-end)/(done-end) : 1
        panel.style.opacity=String(opacity)
        panel.style.visibility=opacity>.01 ? 'visible' : 'hidden'
        const offset=progress<full ? (1-opacity)*20 : -(1-opacity)*20
        panel.style.transform=matchMedia('(max-width: 600px)').matches ? `translateY(${offset}px)` : `translateY(calc(-50% + ${offset}px))`
      })
    }
    updatePanels(0)
    const media=gsap.matchMedia()
    media.add('(prefers-reduced-motion: no-preference)',()=>{
      const update=self=>{
        desired=Math.round(self.progress*(COUNT-1))
        section.current.style.setProperty('--progress',self.progress)
        updatePanels(self.progress);schedule();pump()
      }
      const trigger=ScrollTrigger.create({trigger:section.current,start:'top top',end:'bottom bottom',onUpdate:update,onRefresh:update})
      return ()=>trigger.kill()
    })
    pump()
    return ()=>{disposed=true;media.revert();observer.disconnect();cancelAnimationFrame(raf);cache.clear()}
  },[])
  return <section id="top" className="sequence" ref={section} aria-label="The Aurum Serum story">
    <span id="formula" className="scene-anchor anchor-formula"/><span id="spots" className="scene-anchor anchor-spots"/><span id="result" className="scene-anchor anchor-result"/>
    <div className="film-stage">
      <img className="film-poster" src={`${import.meta.env.BASE_URL}scenes/hero.webp`} alt="Aurum Serum in amber glass surrounded by golden ripples against a burnt-orange backdrop" fetchPriority="high"/>
      <canvas ref={canvas} className="film-canvas" aria-hidden="true"/><div className="film-shade"/>
      <div className="scene-copy intro-copy"><p className="eyebrow">AURUM SERUM · YOUR DAILY RITUAL</p><h1>A little gold.<br/>Every day.</h1><p>A moment of care.<br/>A ritual for radiant-looking skin.</p><a className="pill-button" href="#shop">Discover Aurum <span aria-hidden="true">↗</span></a><a className="underlined" href="#formula">See how it works</a></div>
      <div className="scene-copy formula-copy"><p className="eyebrow">THE FORMULA</p><h2>Golden care,<br/><span>in a dropper.</span></h2><p>Meet your everyday ritual.<br/>Aurum Serum, thoughtfully bottled<br/> in warm amber glass.</p></div>
      <div className="scene-copy spots-copy"><p className="eyebrow">A CLOSER LOOK</p><h2>Real skin.<br/><span>A little more care.</span></h2><p>Take a moment. Get closer.<br/>Make room for a daily ritual.</p></div>
      <div className="scene-copy result-copy"><p className="eyebrow">THE RITUAL</p><h2>A moment for you.<br/><span>Every single day.</span></h2><p>Simple. Considered. Yours.</p><a className="pill-button dark-button" href="#shop">Meet Aurum <span aria-hidden="true">↗</span></a></div>
      <a href="#formula" className="scroll-cue">SCROLL <span aria-hidden="true">↓</span></a><span className="film-caption">LUMORA / AURUM SERUM</span><div className="film-progress" aria-hidden="true"/>
      {failed && <p className="film-error" role="status">Showing the still image. Discover Aurum below.</p>}
    </div>
  </section>
}
