// Loading animation
const shimmer =
  'before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_2s_infinite] before:bg-gradient-to-r before:from-transparent before:via-white/60 before:to-transparent';

export function BaseSkeleton({ children }: { children: React.ReactNode }) {
  return (
    <>
    <div
      className={`${shimmer} flex flex-col relative overflow-hidden rounded-xl bg-gray-100 p-4 shadow-sm h-full w-full max-h-80`}
    >
      <div className="flex px-12 py-2">
        <div className="h-6 w-full rounded-md bg-gray-200" />
      </div>
      <div className="flex flex-col flex-grow items-center justify-center rounded-xl bg-white mt-2 p-2">
        {children}
      </div>
    </div>
    </>
  );
}

export function DonutSkeleton() {
  return (
    <BaseSkeleton>
      {/* Donut chart */}
      <div className="w-[40%] max-w-xs h-auto aspect-square rounded-full bg-transparent bg-transparent border-8 border-gray-200"/>
      {/* Table rows */}
      <div className="flex justify-between p-2 mt-1 w-full">
        <div className="h-4 w-[35%] rounded-md bg-gray-200" />
        <div className="h-4 w-[30%] rounded-md bg-gray-200" />
      </div>
      <div className="flex justify-between p-2 w-full">
        <div className="h-4 w-[40%] rounded-md bg-gray-200" />
        <div className="h-4 w-[35%] rounded-md bg-gray-200" />
      </div>
    </BaseSkeleton>
  );
}

export function BarSkeleton() {
  return (
    <BaseSkeleton>
      {/* Bar chart container */}
      <div className="flex flex-grow items-end justify-between py-2 px-10 mt-1 w-full">
        {/* Vertical bars with varying heights */}
        <div className="w-[5%] h-[40%] bg-gray-200 rounded-md" />
        <div className="w-[5%] h-[50%] bg-gray-200 rounded-md" />
        <div className="w-[5%] h-[60%] bg-gray-200 rounded-md" />
        <div className="w-[5%] h-[70%] bg-gray-200 rounded-md" />
        <div className="w-[5%] h-[80%] bg-gray-200 rounded-md" />
        <div className="w-[5%] h-[90%] bg-gray-200 rounded-md" />
        <div className="w-[5%] h-[85%] bg-gray-200 rounded-md" />
        <div className="w-[5%] h-[75%] bg-gray-200 rounded-md" />
        <div className="w-[5%] h-[65%] bg-gray-200 rounded-md" />
        <div className="w-[5%] h-[55%] bg-gray-200 rounded-md" />
        <div className="w-[5%] h-[45%] bg-gray-200 rounded-md" />
        <div className="w-[5%] h-[35%] bg-gray-200 rounded-md" />
      </div>
    </BaseSkeleton>
  );
}

export function FinKpiSkeleton() {
  return (
    <BaseSkeleton>
      {[...Array(5)].map((_, index) => (
        <div key={index} className="flex justify-between p-2 w-full">
        <div className="h-4 w-[40%] rounded-md bg-gray-200" />
        <div className="h-4 w-[35%] rounded-md bg-gray-200" />
        </div>
      ))}
    </BaseSkeleton>
  );
}

export function FinBarSkeleton() {
  return (
    <BaseSkeleton>
      {/* Bar chart container */}
      <div className="flex flex-grow items-end justify-between py-2 px-20 mt-1 w-full">
        {/* Vertical bars with varying heights */}
        <div className="w-[45%] h-[40%] bg-gray-200 rounded-md" />
        <div className="w-[45%] h-[80%] bg-gray-200 rounded-md" />
      </div>
    </BaseSkeleton>
  );
}

export function LineChartSkeleton() {
  return (
    <BaseSkeleton>
      <div className="flex flex-col flex-grow items-center py-2 px-10 mt-1 w-full">
        {/* First line chart */}
        <div className="flex flex-grow flex-col justify-center items-center p-2 w-full">
          <div className="h-[50%] w-full rounded-md bg-gray-200 m-4" />
          <div className="h-[25%] w-full rounded-md bg-gray-200 m-4" />
        </div>
      </div>
    </BaseSkeleton>
  )
}
