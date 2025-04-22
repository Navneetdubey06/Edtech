document.addEventListener('DOMContentLoaded', function() {
    // Course Progress Chart
    const progressChartElement = document.getElementById('courseProgressChart');
    if (progressChartElement) {
        // Get data from the data attributes
        const labels = JSON.parse(progressChartElement.getAttribute('data-labels'));
        const data = JSON.parse(progressChartElement.getAttribute('data-values'));
        
        new Chart(progressChartElement, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Course Completion (%)',
                    data: data,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                }
            }
        });
    }
    
    // Quiz Results Chart
    const quizResultsChartElement = document.getElementById('quizResultsChart');
    if (quizResultsChartElement) {
        const scores = JSON.parse(quizResultsChartElement.getAttribute('data-scores'));
        const timestamps = JSON.parse(quizResultsChartElement.getAttribute('data-timestamps'));
        const passingScore = parseInt(quizResultsChartElement.getAttribute('data-passing-score'));
        
        new Chart(quizResultsChartElement, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [
                    {
                        label: 'Quiz Scores',
                        data: scores,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 2,
                        pointRadius: 5,
                        pointBackgroundColor: function(context) {
                            const index = context.dataIndex;
                            const value = context.dataset.data[index];
                            return value >= passingScore ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)';
                        }
                    },
                    {
                        label: 'Passing Score',
                        data: new Array(timestamps.length).fill(passingScore),
                        backgroundColor: 'transparent',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                }
            }
        });
    }
    
    // Admin Dashboard - Enrollment Chart
    const enrollmentChartElement = document.getElementById('enrollmentChart');
    if (enrollmentChartElement) {
        const months = JSON.parse(enrollmentChartElement.getAttribute('data-months'));
        const enrollments = JSON.parse(enrollmentChartElement.getAttribute('data-enrollments'));
        
        new Chart(enrollmentChartElement, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Monthly Enrollments',
                    data: enrollments,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                }
            }
        });
    }
    
    // Admin Dashboard - Revenue Chart
    const revenueChartElement = document.getElementById('revenueChart');
    if (revenueChartElement) {
        const months = JSON.parse(revenueChartElement.getAttribute('data-months'));
        const revenue = JSON.parse(revenueChartElement.getAttribute('data-revenue'));
        
        new Chart(revenueChartElement, {
            type: 'bar',
            data: {
                labels: months,
                datasets: [{
                    label: 'Monthly Revenue ($)',
                    data: revenue,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            callback: function(value) {
                                return '$' + value;
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                }
            }
        });
    }
});
