import { useEffect, useRef, useState } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import sequence from './sequenceManifest.json'
import { frameAtProgress } from './sequenceTimeline'
gsap.registerPlugin(ScrollTrigger)
const COUNT = sequence.frameCount
const url = (i) => `${import.meta.env.BASE_URL}${sequence.directory}/frame_${String(i + 1).padStart(4, '0')}.webp?v=${sequence.revision}`
export default function ProductSequence() {
  const section = useRef(null), canvas = useRef(null)
  const [failed, setFailed] = useState(false)
  useEffect(() => {
    const el = canvas.current, ctx = el.getContext('2d', { alpha: false })
    if (!ctx) return
    const reduced = matchMedia('(prefers-reduced-motion: reduce)')
    const mobile = matchMedia('(max-width: 600px)')
    const cacheLimit = mobile.matches ? 16 : 24
    const concurrency = mobile.matches ? 4 : 6
    const cache = new Map(), loading = new Set(), failures = new Set(), requests = new Set()
    let desired = 0, drawn = -1, raf = 0, disposed = false, direction = 1
    const draw = () => {
      raf = 0
      if (disposed || !cache.size) return
      const index = cache.has(desired) ? desired : [...cache.keys()].reduce((a,b) => Math.abs(a-desired) < Math.abs(b-desired) ? a : b)
      if (index === drawn) return
      const image = cache.get(index)
      // Fill every viewport; portrait screens crop around the central action.
      const scale = Math.max(el.width/image.width, el.height/image.height)
      const width = image.width*scale, height = image.height*scale
      const x = (el.width-width)/2
      const y = (el.height-height)/2
      ctx.fillStyle = '#17251c'
      ctx.fillRect(0,0,el.width,el.height)
      ctx.drawImage(image,x,y,width,height)
      el.style.opacity = '1'; el.dataset.frame = String(index+1); drawn = index
      el.dataset.phase = sequence.phases.find(phase => index >= phase.start && index <= phase.end)?.name
    }
    const schedule = () => { if (!raf && !disposed) raf = requestAnimationFrame(draw) }
    const pump = () => {
      if (disposed) return
      const candidates = [desired]
      if (!reduced.matches) {
        // Keep the entire prefetch window inside the decoded cache budget.
        // Otherwise evicted candidates are immediately fetched again forever.
        const radius = Math.floor((cacheLimit-1)/2)
        for(let o=1;o<=radius;o++) {
          candidates.push(desired+o*direction)
          candidates.push(desired-o*direction)
        }
      }
      for(const i of candidates) {
        if(loading.size>=concurrency) break
        if(i<0 || i>=COUNT || cache.has(i) || loading.has(i) || failures.has(i)) continue
        loading.add(i)
        const image = new Image(); image.decoding='async'
        requests.add(image)
        image.onload = async () => {
          let decoded = image
          if (mobile.matches && typeof createImageBitmap === 'function') {
            try { decoded = await createImageBitmap(image) }
            catch { /* Keep the original image if bitmap resizing is unavailable. */ }
          }
          requests.delete(image)
          loading.delete(i)
          if(disposed) { decoded.close?.(); return }
          cache.set(i,decoded)
          const farthest=[...cache.keys()].sort((a,b)=>Math.abs(b-desired)-Math.abs(a-desired))
          while(cache.size>cacheLimit) {
            const index=farthest.shift()
            cache.get(index).close?.()
            cache.delete(index)
          }
          schedule(); pump()
        }
        image.onerror = () => { requests.delete(image); loading.delete(i); failures.add(i); if(!disposed) { if((failures.size>8 || reduced.matches) && !cache.size) setFailed(true); pump() } }
        image.src=url(i)
      }
    }
    const resize = () => {
      const dpr=Math.min(devicePixelRatio||1,2)
      el.width=Math.round(el.clientWidth*dpr); el.height=Math.round(el.clientHeight*dpr)
      ctx.imageSmoothingEnabled=true; ctx.imageSmoothingQuality='high'
      drawn=-1; schedule()
    }
    const observer=new ResizeObserver(resize); observer.observe(el); resize()
    const panels=section.current.querySelectorAll('.scene-copy')
    const updatePanels = (progress) => {
      const windows=[[0,0,.065,.10],[.11,.14,.25,.29],[.37,.40,.64,.69],[.74,.76,.80,.84],[.86,.89,1,1]]
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
        const next=frameAtProgress(self.progress, sequence)
        if(next!==desired) direction=next>desired ? 1 : -1
        desired=next
        section.current.style.setProperty('--progress',self.progress)
        updatePanels(self.progress);schedule();pump()
      }
      const trigger=ScrollTrigger.create({trigger:section.current,start:'top top',end:'bottom bottom',onUpdate:update,onRefresh:update,onToggle:()=>{
        drawn=-1;schedule()
      }})
      return ()=>trigger.kill()
    })
    pump()
    return ()=>{
      disposed=true;media.revert();observer.disconnect();cancelAnimationFrame(raf)
      requests.forEach(image=>{image.onload=image.onerror=null;image.src=''})
      cache.forEach(image=>image.close?.());cache.clear()
    }
  },[])
  return <section id="top" className="sequence" ref={section} aria-label="The Ayurvedic hair oil story">
    <span id="formula" className="scene-anchor anchor-formula"/><span id="craft" className="scene-anchor anchor-craft"/><span id="result" className="scene-anchor anchor-result"/>
    <div className="film-stage">
      <img className="film-poster" src={`${import.meta.env.BASE_URL}${sequence.directory}/poster.webp?v=${sequence.revision}`} alt="An empty ceramic bowl on a sunlit wooden table in a lush garden" fetchPriority="high"/>
      <canvas ref={canvas} className="film-canvas" aria-hidden="true"/><div className="film-shade"/>
      <div className="scene-copy intro-copy"><p className="eyebrow">DR. YOGITHA'S · AYURVEDIC HAIR OIL</p><h1>Rooted<br/>in ritual.</h1><p>A botanical story.<br/>A moment for your hair.</p><a className="pill-button" href="#shop">Discover the oil <span aria-hidden="true">↗</span></a><a className="underlined" href="#formula">Follow the ingredients</a></div>
      <div className="scene-copy formula-copy"><p className="eyebrow">THE BOTANICAL STORY</p><h2>From nature.<br/><span>With care.</span></h2><p>Leaves, flowers and golden tones.<br/>An Ayurvedic-inspired ritual.</p></div>
      <div className="scene-copy filling-copy"><p className="eyebrow">THE GOLDEN POUR</p><h2>A slower<br/><span>kind of care.</span></h2><p>Follow every golden drop.<br/>From the bowl to the bottle.</p></div>
      <div className="scene-copy packaging-copy"><p className="eyebrow">THE FINAL TOUCH</p><h2>Care,<br/><span>beautifully bottled.</span></h2><p>A botanical ritual takes shape.</p></div>
      <div className="scene-copy result-copy"><p className="eyebrow">YOUR HAIR RITUAL</p><h2>Make time<br/><span>for your roots.</span></h2><p>Ayurvedic hair oil.<br/>A little time for yourself.</p><a className="pill-button dark-button" href="#shop">Meet the hair oil <span aria-hidden="true">↗</span></a></div>
      <a href="#formula" className="scroll-cue">SCROLL <span aria-hidden="true">↓</span></a><span className="film-caption">DR. YOGITHA'S / AYURVEDIC HAIR OIL</span><div className="film-progress" aria-hidden="true"/>
      {failed && <p className="film-error" role="status">Showing the still image. Discover the hair oil below.</p>}
    </div>
  </section>
}
