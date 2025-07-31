#include <boost/dll/alias.hpp>
#include <memory>

#include "cartographer/plugin/metrics/prometheus/family_factory.h"
#include "prometheus/exposer.h"

extern "C" BOOST_SYMBOL_EXPORT void* GetFamilyFactory();
extern "C" BOOST_SYMBOL_EXPORT bool StartExposer(const char* addr);

namespace cartographer {
namespace plugin {
namespace metrics {
namespace prometheus {
static std::once_flag once_flag;

class PrometheusMetrics {
 public:
  static PrometheusMetrics& Instance() {
    std::call_once(once_flag,
                   []() { instance = std::make_unique<PrometheusMetrics>(); });

    return *instance;
  }

  metrics::prometheus::FamilyFactory* GetFamilyFactory() {
    return &family_factory;
  }

  bool StartExposer(const char* addr) {
    try {
      if (!exposer) {
        exposer = std::make_unique<::prometheus::Exposer>(addr);
        exposer->RegisterCollectable(family_factory.GetCollectable());
      }
    } catch (const std::exception& e) {
      return false;
    }
    return true;
  }

  PrometheusMetrics() {}

 private:
  metrics::prometheus::FamilyFactory family_factory;
  std::unique_ptr<::prometheus::Exposer> exposer;
  static std::unique_ptr<PrometheusMetrics> instance;
};

std::unique_ptr<PrometheusMetrics> PrometheusMetrics::instance;

}  // namespace prometheus
}  // namespace metrics
}  // namespace plugin
}  // namespace cartographer

using cartographer::plugin::metrics::prometheus::PrometheusMetrics;

void* GetFamilyFactory() {
  return PrometheusMetrics::Instance().GetFamilyFactory();
}

bool StartExposer(const char* addr) {
  return PrometheusMetrics::Instance().StartExposer(addr);
}
