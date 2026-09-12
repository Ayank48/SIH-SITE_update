import { LoaderCircle } from "lucide-react";

export default function WorkspaceLoading() {
  return (
    <main className="min-h-screen flex items-center justify-center px-6 text-fg">
      <div className="panel-float w-full max-w-md p-8 text-center anim-rise">
        <div className="mx-auto h-11 w-11 rounded-xl panel-inset flex items-center justify-center text-accent">
          <LoaderCircle className="h-5 w-5 anim-pulse-soft" />
        </div>
        <p className="eyebrow mt-5 text-accent">Mission workspace</p>
        <h1 className="mt-2 text-lg font-semibold">Preparing analysis instruments</h1>
        <p className="mt-2 text-xs text-muted">Loading the correspondence workspace...</p>
      </div>
    </main>
  );
}