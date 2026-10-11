import { Accordion } from "../components/Accordion";
import { Card } from "../components/Card";

const steps = [
  ["1", "Upload", "You add a photo from your computer, or paste one from the clipboard."],
  ["2", "Look for save differences", "The app re-saves the photo as a JPEG and measures where the pixels change. Edited areas often change more."],
  ["3", "Score the result", "A small neural network reads that difference map and returns a model score for editing."],
];

export default function HowItWorks() {
  return (
    <div className="mx-auto max-w-[1100px] px-5 py-12">
      <h1 className="text-4xl font-semibold tracking-tight">How it works</h1>
      <p className="mt-3 max-w-2xl text-lg text-[#64748B]">Three quiet steps. No lab equipment required.</p>
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {steps.map(([index, title, body]) => (
          <Card key={index}>
            <p className="text-sm font-semibold text-[#4F46E5]">{index}</p>
            <h2 className="mt-2 text-2xl font-semibold">{title}</h2>
            <p className="mt-2 text-[#64748B]">{body}</p>
          </Card>
        ))}
      </div>
      <Card className="mt-6">
        <p className="text-sm text-[#64748B]">What the check looks at</p>
        <div className="mt-4 flex flex-wrap items-center gap-3 text-sm font-medium">
          <span className="rounded-2xl bg-slate-100 px-4 py-3">Image</span>
          <span aria-hidden="true">→</span>
          <span className="rounded-2xl bg-slate-100 px-4 py-3">Difference map</span>
          <span aria-hidden="true">→</span>
          <span className="rounded-2xl bg-[#EEF2FF] px-4 py-3 text-[#4F46E5]">Verdict</span>
        </div>
      </Card>
      <Card className="mt-6">
        <h2 className="text-2xl font-semibold">Limitations</h2>
        <p className="mt-2 text-[#64748B]">
          A normal re-save can look like an edit, and a careful edit can leave almost no trace. The score does not mark which pixels changed, and it cannot prove a photo is real or fake.
        </p>
      </Card>
      <div className="mt-6">
        <Accordion title="Technical details">
          <p className="font-mono text-sm">E(x, y) = |original − resaved JPEG| × scale</p>
          <p className="mt-3 text-sm">
            The network takes a 128×128, 3-channel difference image. Three convolution blocks use 16, 32, and 64 filters, then one score. Training uses binary cross-entropy on the raw score.
          </p>
        </Accordion>
      </div>
    </div>
  );
}
