<?php

use Twig\Environment;
use Twig\Error\LoaderError;
use Twig\Error\RuntimeError;
use Twig\Extension\SandboxExtension;
use Twig\Markup;
use Twig\Sandbox\SecurityError;
use Twig\Sandbox\SecurityNotAllowedTagError;
use Twig\Sandbox\SecurityNotAllowedFilterError;
use Twig\Sandbox\SecurityNotAllowedFunctionError;
use Twig\Source;
use Twig\Template;

/* server/status/advisor/index.twig */
class __TwigTemplate_41c662b7ddcea99b9b19ec63cca05ace7a2a1c8b3d2b797898166e331a59544e extends \Twig\Template
{
    private $source;
    private $macros = [];

    public function __construct(Environment $env)
    {
        parent::__construct($env);

        $this->source = $this->getSourceContext();

        $this->blocks = [
            'content' => [$this, 'block_content'],
        ];
    }

    protected function doGetParent(array $context)
    {
        // line 1
        return "server/status/base.twig";
    }

    protected function doDisplay(array $context, array $blocks = [])
    {
        $macros = $this->macros;
        // line 2
        $context["active"] = "advisor";
        // line 1
        $this->parent = $this->loadTemplate("server/status/base.twig", "server/status/advisor/index.twig", 1);
        $this->parent->display($context, array_merge($this->blocks, $blocks));
    }

    // line 4
    public function block_content($context, array $blocks = [])
    {
        $macros = $this->macros;
        // line 5
        echo "
  <h2>";
        // line 6
        echo _gettext("Advisor system");
        echo "</h2>

  ";
        // line 8
        if (twig_test_empty(($context["data"] ?? null))) {
            // line 9
            echo "    ";
            echo call_user_func_array($this->env->getFilter('error')->getCallable(), [_gettext("Not enough privilege to view the advisor.")]);
            echo "
  ";
        } else {
            // line 11
            echo "    <button type=\"button\" class=\"btn btn-secondary mb-4\" data-toggle=\"modal\" data-target=\"#advisorInstructionsModal\">
      ";
            // line 12
            echo \PhpMyAdmin\Html\Generator::getIcon("b_help", _gettext("Instructions"));
            echo "
    </button>

    <div class=\"modal fade\" id=\"advisorInstructionsModal\" tabindex=\"-1\" role=\"dialog\" aria-labelledby=\"advisorInstructionsModalLabel\" aria-hidden=\"true\">
      <div class=\"modal-dialog\" role=\"document\">
        <div class=\"modal-content\">
          <div class=\"modal-header\">
            <h5 class=\"modal-title\" id=\"advisorInstructionsModalLabel\">";
            // line 19
            echo _gettext("Advisor system");
            echo "</h5>
            <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"";
            // line 20
            echo _gettext("Close");
            echo "\">
              <span aria-hidden=\"true\">&times;</span>
            </button>
          </div>
          <div class=\"modal-body\">
            <p>";
            // line 26
            echo _gettext("The Advisor system can provide recommendations on server variables by analyzing the server status variables.");
            // line 29
            echo "</p>
            <p>";
            // line 31
            echo _gettext("Do note however that this system provides recommendations based on simple calculations and by rule of thumb which may not necessarily apply to your system.");
            // line 34
            echo "</p>
            <p>";
            // line 36
            echo _gettext("Prior to changing any of the configuration, be sure to know what you are changing (by reading the documentation) and how to undo the change. Wrong tuning can have a very negative effect on performance.");
            // line 39
            echo "</p>
            <p>";
            // line 41
            echo _gettext("The best way to tune your system would be to change only one setting at a time, observe or benchmark your database, and undo the change if there was no clearly measurable improvement.");
            // line 44
            echo "</p>
          </div>
          <div class=\"modal-footer\">
            <button type=\"button\" class=\"btn btn-primary\" data-dismiss=\"modal\">";
            // line 47
            echo _gettext("Close");
            echo "</button>
          </div>
        </div>
      </div>
    </div>

    ";
            // line 53
            if ((twig_length_filter($this->env, twig_get_attribute($this->env, $this->source, ($context["data"] ?? null), "errors", [], "any", false, false, false, 53)) > 0)) {
                // line 54
                echo "      <div class=\"alert alert-danger mt-2 mb-2\" role=\"alert\">
        <h4 class=\"alert-heading\">";
                // line 55
                echo _gettext("Errors occurred while executing rule expressions:");
                echo "</h4>
        <ul>
          ";
                // line 57
                $context['_parent'] = $context;
                $context['_seq'] = twig_ensure_traversable(twig_get_attribute($this->env, $this->source, ($context["data"] ?? null), "errors", [], "any", false, false, false, 57));
                foreach ($context['_seq'] as $context["_key"] => $context["error"]) {
                    // line 58
                    echo "            <li>";
                    echo twig_escape_filter($this->env, $context["error"], "html", null, true);
                    echo "</li>
          ";
                }
                $_parent = $context['_parent'];
                unset($context['_seq'], $context['_iterated'], $context['_key'], $context['error'], $context['_parent'], $context['loop']);
                $context = array_intersect_key($context, $_parent) + $_parent;
                // line 60
                echo "        </ul>
      </div>
    ";
            }
            // line 63
            echo "
    ";
            // line 64
            if ((twig_length_filter($this->env, twig_get_attribute($this->env, $this->source, ($context["data"] ?? null), "fired", [], "any", false, false, false, 64)) > 0)) {
                // line 65
                echo "      <h4>";
                echo _gettext("Possible performance issues");
                echo "</h4>

      <div class=\"accordion mb-4\" id=\"rulesAccordion\">
        ";
                // line 68
                $context['_parent'] = $context;
                $context['_seq'] = twig_ensure_traversable(twig_get_attribute($this->env, $this->source, ($context["data"] ?? null), "fired", [], "any", false, false, false, 68));
                $context['loop'] = [
                  'parent' => $context['_parent'],
                  'index0' => 0,
                  'index'  => 1,
                  'first'  => true,
                ];
                if (is_array($context['_seq']) || (is_object($context['_seq']) && $context['_seq'] instanceof \Countable)) {
                    $length = count($context['_seq']);
                    $context['loop']['revindex0'] = $length - 1;
                    $context['loop']['revindex'] = $length;
                    $context['loop']['length'] = $length;
                    $context['loop']['last'] = 1 === $length;
                }
                foreach ($context['_seq'] as $context["_key"] => $context["rule"]) {
                    // line 69
                    echo "          <div class=\"card\">
            <div class=\"card-header\" id=\"heading";
                    // line 70
                    echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["loop"], "index", [], "any", false, false, false, 70), "html", null, true);
                    echo "\">
              <button class=\"btn btn-link";
                    // line 71
                    echo (( !twig_get_attribute($this->env, $this->source, $context["loop"], "first", [], "any", false, false, false, 71)) ? (" collapsed") : (""));
                    echo "\" type=\"button\" data-toggle=\"collapse\" data-target=\"#collapse";
                    echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["loop"], "index", [], "any", false, false, false, 71), "html", null, true);
                    echo "\" aria-expanded=\"";
                    echo ((twig_get_attribute($this->env, $this->source, $context["loop"], "first", [], "any", false, false, false, 71)) ? ("true") : ("false"));
                    echo "\" aria-controls=\"collapse";
                    echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["loop"], "index", [], "any", false, false, false, 71), "html", null, true);
                    echo "\">
                ";
                    // line 72
                    echo twig_escape_filter($this->env, strip_tags(twig_get_attribute($this->env, $this->source, $context["rule"], "issue", [], "any", false, false, false, 72)), "html", null, true);
                    echo "
              </button>
            </div>
            <div id=\"collapse";
                    // line 75
                    echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["loop"], "index", [], "any", false, false, false, 75), "html", null, true);
                    echo "\" class=\"collapse";
                    echo ((twig_get_attribute($this->env, $this->source, $context["loop"], "first", [], "any", false, false, false, 75)) ? (" show") : (""));
                    echo "\" aria-labelledby=\"heading";
                    echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["loop"], "index", [], "any", false, false, false, 75), "html", null, true);
                    echo "\" data-parent=\"#rulesAccordion\">
              <div class=\"card-body\">
                <dl>
                  <dt>";
                    // line 78
                    echo _gettext("Issue:");
                    echo "</dt>
                  <dd>";
                    // line 79
                    echo twig_get_attribute($this->env, $this->source, $context["rule"], "issue", [], "any", false, false, false, 79);
                    echo "</dd>

                  <dt>";
                    // line 81
                    echo _gettext("Recommendation:");
                    echo "</dt>
                  <dd>";
                    // line 82
                    echo twig_get_attribute($this->env, $this->source, $context["rule"], "recommendation", [], "any", false, false, false, 82);
                    echo "</dd>

                  <dt>";
                    // line 84
                    echo _gettext("Justification:");
                    echo "</dt>
                  <dd>";
                    // line 85
                    echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["rule"], "justification", [], "any", false, false, false, 85), "html", null, true);
                    echo "</dd>

                  <dt>";
                    // line 87
                    echo _gettext("Used variable / formula:");
                    echo "</dt>
                  <dd>";
                    // line 88
                    echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["rule"], "formula", [], "any", false, false, false, 88), "html", null, true);
                    echo "</dd>

                  <dt>";
                    // line 90
                    echo _gettext("Test:");
                    echo "</dt>
                  <dd>";
                    // line 91
                    echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["rule"], "test", [], "any", false, false, false, 91), "html", null, true);
                    echo "</dd>
                </dl>
              </div>
            </div>
          </div>
        ";
                    ++$context['loop']['index0'];
                    ++$context['loop']['index'];
                    $context['loop']['first'] = false;
                    if (isset($context['loop']['length'])) {
                        --$context['loop']['revindex0'];
                        --$context['loop']['revindex'];
                        $context['loop']['last'] = 0 === $context['loop']['revindex0'];
                    }
                }
                $_parent = $context['_parent'];
                unset($context['_seq'], $context['_iterated'], $context['_key'], $context['rule'], $context['_parent'], $context['loop']);
                $context = array_intersect_key($context, $_parent) + $_parent;
                // line 97
                echo "      </div>
    ";
            }
            // line 99
            echo "  ";
        }
        // line 100
        echo "
";
    }

    public function getTemplateName()
    {
        return "server/status/advisor/index.twig";
    }

    public function isTraitable()
    {
        return false;
    }

    public function getDebugInfo()
    {
        return array (  282 => 100,  279 => 99,  275 => 97,  255 => 91,  251 => 90,  246 => 88,  242 => 87,  237 => 85,  233 => 84,  228 => 82,  224 => 81,  219 => 79,  215 => 78,  205 => 75,  199 => 72,  189 => 71,  185 => 70,  182 => 69,  165 => 68,  158 => 65,  156 => 64,  153 => 63,  148 => 60,  139 => 58,  135 => 57,  130 => 55,  127 => 54,  125 => 53,  116 => 47,  111 => 44,  109 => 41,  106 => 39,  104 => 36,  101 => 34,  99 => 31,  96 => 29,  94 => 26,  86 => 20,  82 => 19,  72 => 12,  69 => 11,  63 => 9,  61 => 8,  56 => 6,  53 => 5,  49 => 4,  44 => 1,  42 => 2,  35 => 1,);
    }

    public function getSourceContext()
    {
        return new Source("", "server/status/advisor/index.twig", "E:\\STUDENT\\phpMyAdmin\\templates\\server\\status\\advisor\\index.twig");
    }
}
