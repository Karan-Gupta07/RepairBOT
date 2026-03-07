export default function Landing() {
  return (
    <section className="landing">
      <div className="mark" aria-hidden="true">🔧</div>
      <h1>Fix it yourself.</h1>
      <p className="lead">
        Snap a photo of something broken. Get a repair summary, cost estimate,
        and direct links to buy parts and tools.
      </p>
      <div className="steps">
        <div className="step">
          <span className="step-num">1</span>
          <div>
            <h3>Upload a photo</h3>
            <p>Chair, phone, appliance — anything that needs a repair.</p>
          </div>
        </div>
        <div className="step">
          <span className="step-num">2</span>
          <div>
            <h3>Get your report</h3>
            <p>Repairability, estimated cost, and a short description.</p>
          </div>
        </div>
        <div className="step">
          <span className="step-num">3</span>
          <div>
            <h3>Find parts &amp; tools</h3>
            <p>One-click links to search or buy what you need.</p>
          </div>
        </div>
      </div>
      <a href="#app" className="btn-landing">Start a repair</a>
      <p className="landing-footer">
        Images are analyzed by AI and are not stored. Advice is for
        informational purposes only.
      </p>
    </section>
  );
}
