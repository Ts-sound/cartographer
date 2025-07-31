/*
 * Copyright 2018 The Cartographer Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "cartographer/metrics/family_factory.h"
#include "cartographer/metrics/register.h"
// #include "cartographer/plugin/metrics/prometheus/family_factory.h"
#include "glog/logging.h"
#include "gmock/gmock.h"
#include "gtest/gtest.h"
// #include "prometheus/exposer.h"
// #include "prometheus/metric_family.h"

#include <boost/dll/import.hpp>
#include <boost/dll/shared_library.hpp>
#include <iostream>
#include <memory>
#include <thread>

namespace cartographer {
namespace plugin {
namespace metrics {
namespace prometheus {
namespace {

using ::cartographer::metrics::FamilyFactory;

//
class DllFamilyFactory {
 public:
  using GetFamilyFactoryFunc = void*();
  using StartExposerFunc = bool(const char* addr);

 public:
  bool Load(const std::string& library_path) {
    try {
      library_ = boost::dll::shared_library(
          library_path, boost::dll::load_mode::append_decorations);

      auto func = library_.get<GetFamilyFactoryFunc>("GetFamilyFactory");
      family_factory_ = static_cast<FamilyFactory*>(func());

      start_exposer_func_ = library_.get<StartExposerFunc>("StartExposer");
      return true;
    } catch (const std::exception& e) {
      LOG(ERROR) << "Failed to load library: " << e.what();
      return false;
    }
  }

  FamilyFactory* GetFamilyFactory() { return family_factory_; }
  bool StartExposer(const char* addr) { return start_exposer_func_(addr); }

 private:
  boost::dll::shared_library library_;
  FamilyFactory* family_factory_ = nullptr;
  StartExposerFunc* start_exposer_func_ = nullptr;

 private:
};

// using Label = ::prometheus::ClientMetric::Label;

static auto* kCounter = ::cartographer::metrics::Counter::Null();
static auto* kGauge = ::cartographer::metrics::Gauge::Null();
static auto* kScoresMetric = ::cartographer::metrics::Histogram::Null();

const char kLabelKey[] = "kind";
const char kLabelValue[] = "score";
const std::array<double, 5> kObserveScores = {{-1, 0.11, 0.2, 0.5, 2}};

class Algorithm {
 public:
  static void RegisterMetrics(::cartographer::metrics::FamilyFactory* factory) {
    auto boundaries = ::cartographer::metrics::Histogram::FixedWidth(0.05, 20);
    try {
      auto* scores_family = factory->NewHistogramFamily(
          "algorithm_scores", "Scores achieved", boundaries);
      kScoresMetric = scores_family->Add({{kLabelKey, kLabelValue}});

      kCounter = factory->NewCounterFamily("test_counter","test")->Add(
                                     {{kLabelKey, kLabelValue}});
    } catch (const std::exception& e) {
      std::cerr << e.what() << '\n';
    }
  }
  void Run() {
    auto stop_time =
        std::chrono::system_clock::now() ;
        // stop_time += std::chrono::minutes(10);
    while (true) {
      for (double score : kObserveScores) {
        kScoresMetric->Observe(score);
        kCounter->Increment();
        std::chrono::milliseconds duration(500);
        std::this_thread::sleep_for(duration);
      }
      if (std::chrono::system_clock::now() > stop_time) {
        break;
      }
    }
  }
};

TEST(MetricsTest, RunExposerServer) {
  DllFamilyFactory dll_factory;
  dll_factory.Load(
      "/root/ws/cartographer/build/cartographer/plugin/metrics/prometheus/"
      "libplugin_metrics_prometheus.so");
  auto registry = dll_factory.GetFamilyFactory();
  Algorithm::RegisterMetrics(registry);
  // ::cartographer::metrics::RegisterAllMetrics(registry);
  dll_factory.StartExposer("0.0.0.0:9100");

  Algorithm algorithm;
  algorithm.Run();
}

}  // namespace
}  // namespace prometheus
}  // namespace metrics
}  // namespace plugin
}  // namespace cartographer
